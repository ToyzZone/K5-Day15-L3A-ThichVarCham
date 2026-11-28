# Thích Var Chạm — Kute Pro Max: trợ lý Discord học từ câu trả lời của lab coach

Kịch bản trình diễn: [demo 2 phút — B01 và B06](docs/demo-2-phut.md).

Tra thông tin riêng qua API portal giả và MCP: [hướng dẫn chạy hai tiến trình](docs/portal-api-mcp.md).

**Thành viên, lớp, track:** xem [TEAMS.md](TEAMS.md). **Điền TEAMS.md đúng format**: khi chấm và đánh giá, BTC quét file này để ghép điểm cho từng người.

*Lát cắt = phần nhỏ nhất làm xong được trong hackathon: một người dùng · một việc · một quyết định AI · một kết quả.*

---

## Nhóm làm gì, khung làm gì

| Nhóm quyết định và viết | Khung làm sẵn (không cần sửa) |
|---|---|
| Người dùng, pain, bằng chứng, impact (`evidence/`, `spec.md` §1–§2) | — |
| Hình dạng giải pháp, công cụ, prompt, luồng (`spec.md` §4, `codebase/agent.py`, `tools.py`, `ai.py`) | Ghi mọi lần gọi model / công cụ vào trace, cộng token (`codebase/tracing.py`) |
| Bộ câu thử, metric, chuẩn "đạt" (`eval/benchmark.csv`, `eval/metric_spec.yaml`, `spec.md` §7) | Kiểm đủ cột, đủ câu `kho` / `tu_choi`, đủ ≥1/3 câu từ người dùng / data thật (`run.py check`) |
| Chấm cột `pass` theo metric spec | Chạy cả bộ một lệnh, có run ID, model, token từng câu (`run.py eval`) · tính % đạt (`run.py score`) |
| Persona, số người dùng thật, giá model (`cost/personas.yaml`) | Sinh ~50 phiên, chạy thật qua bản chạy thử, tính chi phí / phiên, / task thành công, / tháng 3 kịch bản (`run.py simulate`) |

*Ví dụ track A (ví dụ cỡ, không phải lời giải):* nhóm viết công cụ `search_lesson` tra bài pre-class đã đánh mã đoạn, luồng "tra đoạn → model trả lời kèm mã đoạn, không có thì nói không có", metric "mọi khẳng định có mã đoạn đúng", persona "ôn dồn trước kiểm tra". Khung chạy 25 câu thử ra `run-1.csv`, nhóm chấm `pass`, `score` in % đạt; `simulate` chạy 50 phiên ra chi phí / task thành công cho hai model.

## Chạy trong 3 phút

Bản hiện tại cần **Python 3.10 trở lên**, kết nối mạng để gọi model, và các thư viện trong `requirements.txt` để tra portal qua MCP hoặc chạy Discord.

Lần đầu, tạo môi trường rồi cài thư viện:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Nếu PowerShell chặn kích hoạt, dùng `.\.venv\Scripts\python.exe` thay cho `python` trong mọi lệnh dưới đây. Trên macOS/Linux: `python3 -m venv .venv`, `source .venv/bin/activate`, rồi `python -m pip install -r requirements.txt`.

**Bước 1 — Mở cửa sổ lệnh ngay trong thư mục repo**

| Windows (PowerShell) | macOS |
|---|---|
| Mở thư mục repo bằng File Explorer → bấm vào thanh địa chỉ → gõ `powershell` → Enter | Mở **Terminal** (Cmd + Space, gõ "Terminal") → gõ `cd ` (có dấu cách) → kéo thả thư mục repo vào → Enter |

Gõ `dir` (Windows) hoặc `ls` (macOS / Linux): thấy `run.py` và `README.md` là đang đứng đúng chỗ.

**Bước 2 — Kiểm Python và chạy thử**

| Việc | Windows (PowerShell) | macOS / Linux |
|---|---|---|
| Kiểm Python | `python --version` (không được thì `py --version`) | `python3 --version` |
| Chạy bản chạy thử (chế độ giả, chưa gọi model) | `python run.py` | `python3 run.py` |
| Kiểm bộ câu thử | `python run.py check` | `python3 run.py check` |
| Tạo file `.env` để nối model | `copy .env.example .env` | `cp .env.example .env` |

- Windows: gõ `python` mà mở Microsoft Store hoặc báo không có lệnh → dùng `py`. Chưa có Python: cài từ python.org, **tick "Add python.exe to PATH"**, mở lại PowerShell.
- macOS: báo `command not found: python` là bình thường → dùng `python3`.
- Chỉ sao chép `.env.example` khi chưa có `.env`, tránh ghi đè cấu hình hiện tại. Model giả chỉ kiểm tra luồng, không tính là kết quả eval thật.

**Bước 3 — Cấu hình và chạy AI thật**

Điền vào `.env` bằng key riêng có quyền gọi model và đủ hạn mức; không commit hoặc đưa key vào ảnh/video:

```dotenv
MODEL_PROVIDER=openai
MODEL_NAME=gpt-6-luna
API_KEY=<thay bằng API key của bạn>
PORTAL_API_URL=http://127.0.0.1:8765
PORTAL_TOKENS_FILE=
```

Đây là cấu hình model ghi nhận trong lượt eval hiện có. Có thể đổi provider/model theo [hướng dẫn nối model](docs/connect-model.md); ghi nhận model thực tế trong từng lượt.

Terminal thứ nhất, dùng Python trong môi trường vừa cài và giữ API chạy:

```powershell
python codebase/portal_api.py
```

API tự tạo `runtime/portal_tokens.json` lần đầu; để `PORTAL_TOKENS_FILE` trống dùng đường dẫn mặc định. Không cần điền token portal thủ công. Portal dùng dữ liệu giả, không kết nối hệ thống thật.

Terminal thứ hai, kích hoạt cùng môi trường, chạy:

```powershell
python run.py
```

Nhập `XP được tính thế nào?` rồi Enter; nhận kết quả và thống kê model/token. Thoát bằng Ctrl+C hoặc Enter hai lần trên dòng trống. CLI dùng dữ liệu tài khoản giả trong repo; không cần token Discord để chạy CLI/eval.

**Bước 4 — Thử bộ câu hỏi**

Giữ API ở terminal thứ nhất, tại terminal thứ hai chạy:

```powershell
python run.py check
python run.py eval --try
```

Lượt thử chạy ba câu đầu, ghi `eval/run-try.csv` và `traces/run-try.jsonl` (ghi đè mỗi lần thử). Kiểm tra cột `error` rỗng và có token > 0 ở các câu gọi AI. Câu được code xử lý trực tiếp có thể không gọi model. Sau đó mới chạy `python run.py eval`; chấm cột `pass` theo metric rồi chạy `python run.py score eval/run-N.csv` với đúng file vừa sinh.

Nếu báo HTTP 401: kiểm tra API key; HTTP 402: kiểm tra số dư/hạn mức provider; không nối được portal: kiểm tra terminal API, cổng và môi trường đã cài MCP. Với Discord không trả lời, kiểm tra Message Content Intent, role, kênh và quyền gửi tin. Hướng dẫn chi tiết portal: [API và MCP](docs/portal-api-mcp.md).

Trong README này lệnh viết là `python …`; máy nhóm cần `python3` hay `py` thì gõ thay.

## Chạy bot Discord (Windows PowerShell)

Mở terminal tại thư mục gốc của repo. Lần đầu tạo môi trường và cài thư viện:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Nếu chưa có `.env`, sao chép `.env.example` thành `.env`. Nếu đã có, giữ file
hiện tại. Điền token bot và các ID máy chủ, kênh hỏi đáp, kênh duyệt, vai trò
Learner và Lab Coach vào các biến `DISCORD_*`.

Mỗi lần chạy bot:

```powershell
.\.venv\Scripts\python.exe codebase/discord_bot.py
```

Nếu terminal đã kích hoạt môi trường và hiển thị `(.venv)`, có thể dùng:

```powershell
python codebase/discord_bot.py
```

Giữ terminal mở khi dùng bot. Nhấn **Ctrl+C** để dừng. Sau khi sửa code hoặc
`.env`, dừng rồi chạy lại. Chỉ chạy một tiến trình bot.

Khi thấy `Kute Pro Max đã trực tuyến`, dùng tài khoản có vai trò **Learner**
hoặc **Lab Coach**, gửi trong đúng kênh hỏi đáp đã cấu hình:

```text
!hoi XP được tính thế nào?
```

Cũng có thể mention bot kèm câu hỏi. Coach dùng **Trả lời** vào tin của learner
để tạo đề xuất trong kênh duyệt, rồi chọn **Duyệt** hoặc **Bỏ qua**.
Nếu bot không phản hồi, xem log terminal để kiểm tra đúng kênh, vai trò và quyền gửi tin.

Nếu terminal báo `Model: fake`, bot đang ở chế độ thử, chưa trả lời bằng AI thật.

## Lệnh

| Lệnh | Làm gì |
|---|---|
| `python run.py` | Chạy bản chạy thử (gõ đầu vào, nhận kết quả, kèm số lần gọi model / token) |
| `python run.py check` | Kiểm `eval/benchmark.csv` (6 cột, số câu, `kho` / `tu_choi`, mã `source`, ô trống, dòng mẫu) `eval/metric_spec.yaml` (≥3 metric điền đủ) và `TEAMS.md` (đúng format để BTC quét). Chỉ cảnh báo, không sửa file |
| `python run.py eval --try` | **Thử nối model:** chạy 3 câu đầu (`--try 5` = 5 câu) → `eval/run-try.csv`. Thấy "Nối model được" là xong. Không tính là một lượt |
| `python run.py eval` | Chạy cả bộ qua `codebase/agent.py` → `eval/run-1.csv` (lần sau `run-2.csv`…) + `traces/run-1.jsonl`. Mỗi dòng có run ID, model, số lần gọi model / công cụ, token. Model còn giả → chỉ ghi `run-mock.csv`; mọi câu lỗi → `run-error.csv`; Ctrl+C → `run-stopped.csv` — đều **không** được đánh số |
| `python run.py eval --fake` | Thử riêng bộ chạy, không gọi agent → `eval/run-fake.csv` |
| `python run.py score eval/run-1.csv` | Sau khi điền cột `pass` (1 / 0): in % đạt tổng và theo `type`. Còn ô trống → "CHƯA CHẤM XONG", không in % |
| `python run.py simulate --try` | Thử mô phỏng chi phí 10 phiên (làm trước CP3) → `cost/simulate-try.csv` |
| `python run.py simulate` | Mô phỏng chi phí khi dùng thật theo `cost/personas.yaml` (≥50 phiên) → `cost/simulate-N.csv` + `cost/simulate-N-summary.md` |
| `python run.py simulate --rate-from eval/run-2.csv` | Như trên, lấy tỉ lệ đạt từ đúng lượt chỉ định. Không ghi thì khung lấy lượt `run-N` mới nhất đã chấm, cùng model, và ghi rõ đã lấy lượt nào trong bản tóm tắt |

Gói miễn phí báo hết lượt: thêm `--wait 4` sau `eval` hoặc `simulate` (nghỉ 4 giây giữa hai lượt gọi). Sửa CSV bằng Excel: *File → Save As → CSV UTF-8*; Google Sheets: *Tệp → Tải xuống → CSV*.

**Chạy test:** `python -m unittest discover -s codebase` cần đã cài `requirements.txt` và API portal giả đang chạy ở terminal khác (`python codebase/portal_api.py`); thiếu một trong hai thì ba test tra portal trượt. `python -m unittest discover -s evidence` và `python -m unittest test_progress` không cần gì thêm.

**Lượt có lỗi kỹ thuật** (cột `error` có chữ): không sửa tay file đó, chạy lại thành lượt mới và ghi vào bảng các lượt ở `eval/README.md`. Không xoá file lượt nào.

Nhóm dùng stack khác (Node, Streamlit, notebook…): sửa hàm `run_app()` trong `run.py` để `python run.py` vẫn chạy được bản chạy thử, và giữ `answer()` trong `codebase/agent.py` để `eval`, `simulate` chạy được.

## Bản chạy thử — viết ở đâu

| File | Viết gì | Bước guide |
|---|---|---|
| `codebase/agent.py` | `answer(text)` — luồng chính, đúng hình dạng ở `spec.md` §4. Khung có sẵn một workflow 2 bước *ví dụ* | 3.2 |
| `codebase/tools.py` | Công cụ của bài toán, mỗi công cụ một hàm có `@tool` | 2.2, 3.2 |
| `codebase/ai.py` | `call_model(system, user)` — chỗ duy nhất gọi model. Chưa điền `.env` thì chạy **chế độ giả** | 3.3 |

- **Trước CP2:** để chế độ giả, công cụ trả dữ liệu giả — `python run.py` đi hết luồng là đủ.
- **Trước CP3:** nối model thật theo [docs/connect-model.md](docs/connect-model.md), `eval --try` thấy token > 0 rồi mới `eval`.
- Bộ chạy gửi **nguyên ô `input`** của câu thử vào `answer(text)`. Dữ liệu nền (bài học, thông báo, lịch…) để trong `data/`, đọc qua công cụ.

## Phần nào thật, phần nào giả

| Thành phần | Thật / Giả | Ghi chú |
|---|---|---|
| Lời gọi AI ở quyết định trung tâm | Thật trong lượt eval đã ghi | Model `gpt-6-luna`; xem `eval/run-1.csv`, `eval/run-2.csv` |
| Bot Discord, ticket và duyệt kiến thức | Chức năng chạy trên server thử nghiệm | Coach duyệt trước khi kiến thức được lưu; learner xác nhận trước khi gửi ticket |
| Portal qua HTTP API và MCP | Dữ liệu giả, lời gọi API/MCP thật | `data/portal_gia.json`, chỉ tra hồ sơ của người hỏi đã liên kết |
| Kho và thông báo | Dữ liệu mẫu trong repo và kiến thức coach duyệt | Không đồng nghĩa thông báo chính thức mới nhất của khóa thật |

## Kết quả lượt 1 và lượt 2

Đối chiếu từ file trong repo ngày 28/11/2026. Hai lượt chạy cùng 30 câu, cùng model `gpt-6-luna`, cùng cách chấm; cột `error` của cả hai lượt đều trống.

| Lượt | Bằng chứng | Đạt / tổng | `thuong` | `kho` | `tu_choi` | Câu trượt |
|---|---|---|---|---|---|---|
| 1 | [CSV](eval/run-1.csv), [trace](traces/run-1.jsonl), run ID `run-1@20261127-222949` | 28/30 (93,3%) | 7/7 | 16/18 | 5/5 | B13, B20 |
| 2 | [CSV](eval/run-2.csv), [trace](traces/run-2.jsonl), run ID `run-2@20261127-233031` | 28/30 (93,3%) | 7/7 | 16/18 | 5/5 | B13, B16 |

Cả hai lượt chưa đạt ngưỡng tổng 95% (cần ít nhất 29/30). Giữa hai lượt nhóm sửa một lần: tra kho trước khi hỏi lại. B20 từ trượt thành đạt, B16 từ đạt thành trượt, B13 vẫn trượt vì trả `them` thay cho `sua`. Kết quả và chuẩn chấm giữ nguyên. Phân tích lỗi ở [báo cáo eval](eval/report.md), bảng các lượt ở [eval/README.md](eval/README.md).

Chi phí: khoảng 0,00036 USD cho mỗi task thành công với `gpt-6-luna`, tính từ 50 phiên mô phỏng và tỉ lệ đạt 28/30 của lượt 2. Xem [báo cáo chi phí](cost/cost-estimate.md).

## Slide và video demo

- Slide nộp: [demo-slides.pdf](demo-slides.pdf), 8 trang. Mỗi trang lấy số từ file nào: [dàn slide](slides/outline.md).
- Kịch bản trình diễn: [demo 2 phút](docs/demo-2-phut.md).
- Video bản chạy thử gọi AI thật (nộp ở CP3): https://youtu.be/S-avUQCneFU
- Video demo dự phòng (nộp ở CP4): https://www.youtube.com/watch?v=YzkiyOrKke0

## Dùng AI vào việc gì

Nhóm dùng Codex hỗ trợ thiết kế, viết và sửa bot Discord, SQLite, API/MCP, prompt và tài liệu; model runtime hỗ trợ trả lời và soạn đề xuất kiến thức.
Người vận hành chạy thử, báo lỗi và xác nhận yêu cầu; learner quyết định gửi ticket, Lab Coach quyết định duyệt kiến thức. AI hỗ trợ chấm B01–B15 nhưng người chấm cần duyệt theo metric đã khóa.
Chi tiết và phần còn cần xác nhận: [khai báo dùng AI](docs/ai-usage.md). Coding agent đọc [AGENTS.md](AGENTS.md).

## File mẫu — điền ở bước nào

| File | Điền ở bước guide | Mốc |
|---|---|---|
| `TEAMS.md` | 1.0 | CP1 · **đúng format**, BTC quét khi chấm |
| `canvas.md` | 1.4 | CP1, cập nhật CP2 |
| `evidence/hypothesis.md` | 1.1 | trước khi tìm bằng chứng |
| `evidence/data-mining.md` · `evidence/interviews/TEMPLATE.md` → `P1.md`… · `evidence/survey/TEMPLATE.md` | 1.2 | bắt đầu sau Zoom, xong CP3 |
| `evidence/summary.md` | 1.2 | CP3 |
| `spec.md` | §0–§2: 1.1–1.3 · §3–§5: 2.1–2.3 · §7: 2.4 · §8: 4.2 · §10: suốt | §7 chốt CP2 · §0–§7 CP3 · đủ CP4 |
| `data/DATA_CARD.md` | 2.4 | bản đầu CP2 |
| `eval/benchmark.csv` · `eval/metric_spec.yaml` | 2.4 | ≥10 câu + metric chốt CP2 · 20–30 câu CP3 |
| `codebase/` | 3.2, 3.3 | khung CP2 · AI thật CP3 |
| `eval/report.md` · `eval/README.md` | 4.1 (README mục 1–4 từ 2.4) | CP4 |
| `cost/personas.yaml` · `cost/cost-estimate.md` | 4.2 | thử 10 phiên CP3 · đủ CP4 |
| `validation/log.md` *(bonus)* | 4.3 | CP4 |
| `slides/outline.md` → `demo-slides.pdf` | 5.1 | CP4 |
| `reflection/TEMPLATE.md` → `reflection/<ten>.md` | 5.3 | 23:59 Thứ Bảy 28/11 |
| `AGENTS.md` · `docs/ai-usage.md` | khi dùng coding agent / AI | suốt |

## Bảy hạng mục bắt buộc — nằm ở file nào

| # | Hạng mục | File |
|---|---|---|
| 1 | Bằng chứng pain | `evidence/` (tổng hợp ở `evidence/summary.md`) |
| 2 | Impact có số | `spec.md` §2 |
| 3 | Thiết kế giải pháp | `spec.md` §4 |
| 4 | Bản chạy thử làm trọn lát cắt | `codebase/` · lệnh ở mục "Lệnh" |
| 5 | Định nghĩa "tốt" + bộ câu thử | `data/DATA_CARD.md` · `eval/` |
| 6 | Mô phỏng chi phí khi dùng thật | `cost/` |
| 7 | Slide + demo + video dự phòng | [demo-slides.pdf](demo-slides.pdf) · [kịch bản demo](docs/demo-2-phut.md) · link video ở mục "Slide và video demo" |
| + | *Bonus:* người dùng thử | `validation/log.md` |
