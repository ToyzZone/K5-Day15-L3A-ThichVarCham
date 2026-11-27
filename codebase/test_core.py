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
truoc = open(agent.__file__.replace("codebase/agent.py", "data/kho_kien_thuc.json"), encoding="utf-8").read()
kich_ban({"loai": "them", "ly_do": "ok", "cau_hoi": "q", "tra_loi": "a"})
kq = ra(json.dumps({"loai": "tra_loi", "kenh": "hoi-dap", "nguoi_gui": "dc_9001", "link": "discord://m1", "cau_hoi": "nộp trễ standup có XP không", "noi_dung": "không"}))
assert kq["trang_thai"] == "cho_duyet" and kq["ban_nhap"]["nguon"] == "discord://m1", kq
assert truoc == open(agent.__file__.replace("codebase/agent.py", "data/kho_kien_thuc.json"), encoding="utf-8").read()

# 5. Model trả rác (như AI giả) → luồng vẫn đi hết: câu hỏi thì chuyển lab coach, đề xuất thì cảnh báo.
kich_ban()
assert ra(hoi("hoi-dap", "dc_1001", "gì đó"))["hanh_dong"] == "chuyen_lab_coach"
kich_ban()
assert ra(json.dumps({"loai": "tra_loi", "nguoi_gui": "dc_9001", "link": "l", "cau_hoi": "a", "noi_dung": "b"}))["loai"] == "canh_bao"

print("OK: 5 nhóm kiểm đều qua")
