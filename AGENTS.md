# AGENTS.md — hướng dẫn cho coding agent (Claude Code, Cursor, Codex…) làm việc trong repo này

> Ôn lại: ngày 12 · lab ngày 12. Nhóm sửa file này cho khớp bài của mình (thêm quy ước riêng, bỏ dòng không dùng).

## Repo này là gì

Repo nộp bài hackathon AI20K của nhóm: một bản chạy thử AI cho **một lát cắt** (xem `spec.md` §4), kèm bằng chứng, bộ câu thử và mô phỏng chi phí. Mọi câu trả lời phải chạy được bằng các lệnh dưới đây.

## Lệnh

```
python run.py                    # chạy bản chạy thử
python run.py check              # kiểm eval/benchmark.csv + eval/metric_spec.yaml
python run.py eval --try         # thử 3 câu đầu
python run.py eval               # chạy cả bộ → eval/run-N.csv + traces/run-N.jsonl
python run.py score eval/run-N.csv
python run.py simulate --try     # thử mô phỏng chi phí 10 phiên
python run.py simulate           # mô phỏng chi phí → cost/simulate-N.csv
```

Khung chỉ dùng thư viện chuẩn của Python. Thêm thư viện thì ghi vào `requirements.txt`.

## Cấu trúc code

| File | Ai sửa | Hợp đồng |
|---|---|---|
| `codebase/agent.py` | nhóm | `answer(text) -> {"output": str}` — luồng chính, đúng hình dạng ở `spec.md` §4 |
| `codebase/ai.py` | nhóm | `call_model(system, user) -> {"text", "model", "tokens_in", "tokens_out"}`, giữ `@model_call`. Token lấy từ `usage` của API, không ước lượng |
| `codebase/tools.py` | nhóm | mỗi công cụ một hàm có `@tool`, docstring: tên · input · output · có tác động ra ngoài không |
| `codebase/tracing.py`, `eval/run_eval.py`, `cost/simulate.py`, `run.py` | **khung — không sửa** | ghi trace, chạy bộ câu thử, mô phỏng chi phí |

## Luật — agent KHÔNG được làm

- Không commit `.env`, API key, dữ liệu cá nhân thật, nguyên file data BTC cấp.
- Không sửa `eval/run-*.csv`, `cost/simulate-*.csv`, `traces/*` đã chạy (trừ điền cột `pass`, `ghi_chu`).
- Không sửa chuẩn "đạt" (`spec.md` §7), `eval/metric_spec.yaml` sau CP2; không xoá câu thử trượt, không sửa `expected` cho khớp output.
- Không bịa người được phỏng vấn, trích dẫn, câu trả lời khảo sát, số liệu. Số không có nguồn thì ghi rõ *(tự ước tính)*.
- Công cụ có tác động ra ngoài (gửi tin, sửa dữ liệu, chấm điểm): chỉ tạo bản nháp chờ người duyệt.
- Không viết prompt "giấu" câu thử vào code (vd so khớp nguyên văn input của bộ câu thử).

## Nộp checkpoint

Link form của BTC, mã từng ô và lệnh gửi nằm ở [`docs/nop-checkpoint.md`](docs/nop-checkpoint.md). Chỉ gửi form khi đội trưởng nói gửi; gửi xong cập nhật bảng tình trạng trong file đó.

## Quy ước của nhóm

- Ngôn ngữ trả lời người dùng: __
- Ngôn ngữ: code viết bằng tiếng Anh (tên biến/hàm, comment, docstring); code nhóm viết trong `codebase/` và `evidence/` đã đổi hết sang tiếng Anh tối 27/11. Những thứ sau giữ tiếng Việt, vì là chữ cho người đọc hoặc là hợp đồng mà bộ câu thử và `eval/metric_spec.yaml` (đã khoá) dựa vào:
  - prompt, chữ hiện cho người dùng, ghi chú `note()` trong trace;
  - khoá và giá trị JSON của sự kiện, của output và của file trong `data/` (`hanh_dong`, `loai`, `ban_nhap`…);
  - tên công cụ có `@tool` (`tra_kho_kien_thuc`, `tra_thong_bao`, `tra_portal`, `tao_ticket`): trace ghi tên hàm, metric nhắc `tra_portal`.
  File khung của BTC (`codebase/tracing.py`, `codebase/app.py`, `run.py`, `eval/run_eval.py`, `cost/simulate.py`) giữ như bản gốc. Script đếm đã công bố số (`evidence/count.py`) chỉ được đổi tên hoặc dịch chữ khi output trên dữ liệu thô trước và sau giống từng byte, và phải ghi lại ở `evidence/data-mining.md`.
  Docs, ghi chú, file `.md` viết bằng tiếng Việt.
- Test: mỗi thay đổi code đi kèm test mới, dùng `unittest` (thư viện chuẩn). Test của `codebase/` đặt ở `codebase/test_<module>.py`; test của script trong `evidence/` đặt cạnh script (`evidence/test_<tên>.py`). Chạy `python -m unittest discover -s codebase` và `python -m unittest discover -s evidence`, thấy `OK` rồi mới báo xong. Test không gọi model thật: thay `agent.call_model` bằng một kịch bản trả lời định sẵn (xem `codebase/test_agent.py`).
- Sửa test: agent không tự sửa hay xoá test đã có, kể cả chỉnh assert hay giá trị mong đợi cho khớp code mới. Cần sửa thì nêu test nào, sửa gì, vì sao, rồi chờ người dùng xác nhận mới sửa. Thêm test mới thì không cần hỏi.
- Ai duyệt thay đổi do agent tạo trước khi commit: __
