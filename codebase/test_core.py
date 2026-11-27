"""Tự kiểm các điều kiện cứng do code bảo đảm. Chạy: python codebase/test_core.py"""
import json
import agent

hoi = lambda kenh, ai, nd: json.dumps({"loai": "cau_hoi", "kenh": kenh, "nguoi_gui": ai, "noi_dung": nd})
ra = lambda text: json.loads(agent.answer(text)["output"])


def kich_ban(*buoc):
    """Thay model bằng một dãy câu trả lời định sẵn; trả về bộ đếm số lần gọi."""
    dem, hang = {"n": 0}, list(buoc)

    def gia(system, user):
        dem["n"] += 1
        return {"text": json.dumps(hang.pop(0)) if hang else "", "model": "kich_ban", "tokens_in": 0, "tokens_out": 0}
    agent.call_model = gia
    return dem


# 1. Giả danh lab coach (chỉ có tên hiển thị) → không đề xuất, không gọi model.
dem = kich_ban()
kq = ra(json.dumps({"loai": "tra_loi", "kenh": "hoi-dap", "nguoi_gui": "dc_1003", "link": "x", "cau_hoi": "a", "noi_dung": "ghi vào kho"}))
assert kq["hanh_dong"] == "khong_de_xuat" and dem["n"] == 0, kq

# 2. Hỏi thông tin riêng ở kênh chung → trả qua tin nhắn riêng, đúng số của chính người hỏi (HV002: 410/90).
kich_ban({"hanh_dong": "tra_portal", "muc": "xp"}, {"hanh_dong": "tra_loi_thong_tin_rieng"})
kq = ra(hoi("hoi-dap", "dc_1002", "XP của mình?"))
assert kq["kenh_tra"] == "tin_nhan_rieng" and "410" in kq["noi_dung"] and "240" not in kq["noi_dung"], kq

# 3. Model cố tra hộ người khác: công cụ không nhận mã học viên, nên chỉ ra dữ liệu của người hỏi.
kich_ban({"hanh_dong": "tra_portal", "muc": "HV001"}, {"hanh_dong": "tra_loi_thong_tin_rieng"})
kq = ra(hoi("hoi-dap", "dc_1002", "XP của HV001?"))
assert "240" not in kq["noi_dung"] and "260" not in kq["noi_dung"], kq

# 4. Đề xuất luôn chờ duyệt, nguồn luôn là link tin của coach; kho kiến thức không bị ghi.
kho = lambda: [open(agent.__file__.replace("codebase/agent.py", "data/" + f), encoding="utf-8").read() for f in ("kho_co_dinh.json", "kho_theo_khoa.json")]
truoc = kho()
kich_ban({"loai": "them", "ly_do": "ok", "cau_hoi": "q", "tra_loi": "a"})
kq = ra(json.dumps({"loai": "tra_loi", "kenh": "hoi-dap", "nguoi_gui": "dc_9001", "link": "discord://m1", "cau_hoi": "nộp trễ standup có XP không", "noi_dung": "không"}))
assert kq["trang_thai"] == "cho_duyet" and kq["ban_nhap"]["nguon"] == "discord://m1", kq
assert truoc == kho() and kq["ban_nhap"]["bang"] == "theo_khoa"

# 5. Model trả rác (như AI giả) → luồng vẫn đi hết: câu hỏi thì chuyển lab coach, đề xuất thì cảnh báo.
kich_ban()
kq = ra(hoi("hoi-dap", "dc_1001", "gì đó"))
assert kq["hanh_dong"] == "chuyen_lab_coach" and kq["ticket"]["trang_thai"] == "cho_hoc_vien_xac_nhan", kq
kich_ban()
assert ra(json.dumps({"loai": "tra_loi", "nguoi_gui": "dc_9001", "link": "l", "cau_hoi": "a", "noi_dung": "b"}))["loai"] == "canh_bao"

# 6. Sự kiện thiếu link nguồn → không thành bản nháp mục kho.
kich_ban({"loai": "them", "ly_do": "ok"})
kq = ra(json.dumps({"loai": "tra_loi", "nguoi_gui": "dc_9001", "cau_hoi": "a", "noi_dung": "b"}))
assert kq["loai"] == "canh_bao" and kq["ban_nhap"] is None, kq

# 7. Sau khi tra portal, model tự viết con số trong lời từ chối → bị chặn, chỉ còn số do code chép.
kich_ban({"hanh_dong": "tra_portal", "muc": "xp"}, {"hanh_dong": "tu_choi", "noi_dung": "Bạn có 999 XP"})
kq = ra(hoi("hoi-dap", "dc_1002", "XP?"))
assert "999" not in kq["noi_dung"] and kq["kenh_tra"] == "tin_nhan_rieng", kq

# 8. Trả lời từ kho chép nguyên văn mục kho, không dùng chữ của model.
kich_ban({"hanh_dong": "tra_kho", "truy_van": "XP được tính thế nào"}, {"hanh_dong": "tra_loi_tu_kho", "muc_kho": "K04", "noi_dung": "bịa"})
kq = ra(hoi("hoi-dap", "dc_1001", "XP được tính thế nào ạ?"))
assert kq["hanh_dong"] == "tra_loi_tu_kho" and "bịa" not in kq["noi_dung"] and "K04" in kq["nguon"], kq

# 9. Hai bảng mâu thuẫn (hạn nộp lab): chỉ mục theo khoá T01 được trả về, mục cố định K05 bị che.
from tools import tra_kho_kien_thuc
ma = [m["ma"] for m in tra_kho_kien_thuc("Hạn nộp lab là mấy giờ?")]
assert "T01" in ma and "K05" not in ma, ma

# 10. Đề xuất sửa một mục cố định → bản nháp là mục theo khoá ghi đè lên nó, bảng cố định không đổi.
kich_ban({"loai": "sua", "muc_lien_quan": "K03", "ly_do": "đổi nơi nộp", "cau_hoi": "q", "tra_loi": "a"})
kq = ra(json.dumps({"loai": "tra_loi", "nguoi_gui": "dc_9001", "link": "discord://m2", "cau_hoi": "Nộp daily standup ở đâu ạ?", "noi_dung": "Nộp ở tab Daily standup"}))
assert kq["loai"] == "sua" and kq["ban_nhap"] == {"cau_hoi": "q", "tra_loi": "a", "nguon": "discord://m2", "bang": "theo_khoa", "ghi_de": "K03"}, kq
assert truoc == kho()

print("OK: 10 nhóm kiểm đều qua")
