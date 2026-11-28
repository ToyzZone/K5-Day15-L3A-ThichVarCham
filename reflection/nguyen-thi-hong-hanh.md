# Reflection — Nguyễn Thị Hồng Hạnh

1. Vai trò + phần mình làm (trỏ tới file / commit):

   Mình phụ trách phần chấm tự động và chi phí. Mình viết script chấm [`eval/grade.py`](../eval/grade.py) kèm 22 test [`eval/test_grade.py`](../eval/test_grade.py) (#24, PR #72): script đọc `eval/run-N.csv`, tách `pass_criterion` thành từng điều kiện, tự chấm phần so được bằng code và tách riêng câu cần người xem; in 4 metric của [`metric_spec.yaml`](../eval/metric_spec.yaml).
   Mình cũng làm phần chi phí: điền 3 persona từ số đếm ở [`data-mining.md` mục 3f](../evidence/data-mining.md) (PR #73) và chạy mô phỏng 50 phiên với gpt-6-luna, 0 lỗi (PR #74). Hiếu làm song song bản đúng flow hơn (chạy sau bản cải tiến và lượt 2, có chi phí / task thành công), nên mình đề xuất nhóm dùng bản của Hiếu cho #43–#46 và đóng hai PR của mình để repo không có hai lượt mô phỏng trùng nhau.
   Mình gán nhãn lô 1 câu trả lời của Kute (#34) bằng [`evidence/label-tool.html`](../evidence/label-tool.html) theo luật ở [`data-mining.md` mục 3g](../evidence/data-mining.md): chấm đủ 249/249 câu, gồm 20 câu chung với lô của Hiếu để đo độ khớp giữa hai người chấm. File lô và file nhãn có tin nhắn Discord thật nên chỉ gửi riêng cho đội trưởng, không đưa lên repo.

2. AI hỗ trợ mình thế nào (việc gì, công cụ gì, chỗ nào phải sửa lại output AI):

   Mình dùng Claude Code hỗ trợ viết code và test, chạy lệnh; mình duyệt từng bước, tự commit và tạo PR.
   Lần chạy đầu, script chấm cho metric `de_xuat_dung_loai` chỉ 2/11 — thấp bất thường. Kiểm lại thì do code đọc lẫn dấu `;` vào giá trị `loai`; sửa xong ra 10/11, và thêm test để lỗi không quay lại.
   Chỗ phải sửa lớn hơn là quy trình: mô phỏng chi phí được chạy khi `personas.yaml` còn giá và số người dùng mẫu, và trước khi có bản cải tiến #42, nên bảng tiền trong `simulate-1-summary.md` không dùng được. Bài học: đọc lại hướng dẫn của đề (điền đủ đầu vào → chạy → chép bảng) trước khi chạy lệnh tốn phí, không chỉ đối chiếu mục "Xong khi" của issue.

3. Một câu thử trượt của nhóm và mình học được gì từ nó:

   B16 ("ai chấm bài?", thiếu thông tin) ở lượt 1 trả `hoi_lai` đúng, nhưng ở lượt 2, sau bản sửa cho B20, lại soạn ticket chuyển lab coach (`chuyen_lab_coach`). Bản sửa giải được B20 nhưng làm hỏng B16, nên tổng vẫn 28/30.
   Script chấm bắt được B16 tự động vì điều kiện `hanh_dong = hoi_lai` so được bằng code; 2 câu trượt script tìm ra ở cả hai lượt (lượt 1: B13, B20; lượt 2: B13, B16) trùng với kết quả người chấm tay. [`run-1.csv`](../eval/run-1.csv) · [`run-2.csv`](../eval/run-2.csv)
   Mình học được hai điều: sửa một lỗi phải chạy lại cả bộ câu thử, không chỉ câu đang sửa; và `pass_criterion` viết được dạng so sánh (`trường = giá trị`) thì chấm lại nhanh và không cãi nhau. 9–10 câu còn lại có điều kiện kiểu "không hứa sẽ duyệt" vẫn phải người xem.
