"""Công cụ của trợ lý Discord — khớp bảng công cụ ở spec.md §4.

Mỗi công cụ là một hàm có @tool. Dữ liệu đọc từ data/ (mô tả ở data/DATA_CARD.md).
Không công cụ nào ghi vào kho kiến thức: mục kho chỉ có hiệu lực sau khi lab coach duyệt.
"""
import contextvars
import json
import os
import re

from tracing import tool, TOOLS  # noqa: F401

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

# Danh tính người hỏi. Code đặt từ tài khoản gửi tin (agent.py); model không có đường nào sửa,
# vì không công cụ nào nhận mã học viên làm tham số.
NGUOI_HOI = contextvars.ContextVar("nguoi_hoi", default=None)
KHO_RUNTIME = contextvars.ContextVar("kho_runtime", default=None)

MUC_PORTAL = ("xp", "diem_danh", "daily_standup", "gate", "deadline", "coach_phu_trach")


def _doc(ten):
    with open(os.path.join(DATA, ten), encoding="utf-8") as f:
        return json.load(f)


def tai_khoan(discord_id):
    """Tra bảng ghép tài khoản Discord → vai trò, mã học viên. Không phải công cụ của model."""
    return next((t for t in _doc("tai_khoan.json") if t["discord_id"] == discord_id), None)


# ponytail: so khớp từ khoá. Đổi sang embedding khi eval trượt vì tra sót.
_BO_QUA = set("là khi nào ạ mình bạn có được không thì và ở của cho với nhỉ vậy đi giúp à nhé các em".split())


def _tu(van_ban):
    return {t for t in re.findall(r"\w+", van_ban.lower()) if t not in _BO_QUA and len(t) > 1}


def _xep(truy_van, cac_muc, lay_chu, k=3):
    q = _tu(truy_van)
    cham = sorted(((len(q & _tu(lay_chu(m))), m) for m in cac_muc), key=lambda x: -x[0])
    return [m for diem, m in cham[:k] if diem >= 2]


@tool
def tra_kho_kien_thuc(cau_hoi: str) -> list:
    """Tra kho kiến thức (chỉ mục đang hiệu lực, đã được lab coach duyệt).
    Input: câu hỏi (str). Output: tối đa 3 mục {"ma", "cau_hoi", "tra_loi", "nguon"}; [] nếu không có.
    Không tác động ra ngoài."""
    runtime = KHO_RUNTIME.get()
    muc = [m for m in (runtime if runtime is not None else _doc("kho_kien_thuc.json")) if m["trang_thai"] == "hieu_luc"]
    return [{k: m[k] for k in ("ma", "cau_hoi", "tra_loi", "nguon")}
            for m in _xep(cau_hoi, muc, lambda m: m["cau_hoi"] + " " + m["tra_loi"])]


@tool
def tra_thong_bao(cau_hoi: str) -> list:
    """Tra thông báo chính thức của khoá.
    Input: câu hỏi (str). Output: tối đa 3 thông báo {"ma", "ngay", "noi_dung", "link"}; [] nếu không có.
    Không tác động ra ngoài."""
    return _xep(cau_hoi, _doc("thong_bao.json"), lambda m: m["noi_dung"])


@tool
def tra_portal(muc: str) -> dict:
    """Tra một mục thông tin riêng của CHÍNH người hỏi trên portal giả.
    Input: tên mục, một trong xp · diem_danh · daily_standup · gate · deadline · coach_phu_trach.
    Output: {"muc", "du_lieu"} hoặc {"loi"}. Không tác động ra ngoài.
    Còn giả ở CP2: đọc thẳng data/portal_gia.json; sau CP2 gọi qua MCP."""
    ma = NGUOI_HOI.get()
    ho_so = _doc("portal_gia.json").get(ma) if ma else None
    if ho_so is None:
        return {"loi": "không xác định được người hỏi"}
    if muc not in MUC_PORTAL:
        return {"loi": "không có mục %r; chỉ có: %s" % (muc, ", ".join(MUC_PORTAL))}
    return {"muc": muc, "du_lieu": ho_so[muc]}


@tool
def chuyen_lab_coach(tom_tat: str) -> dict:
    """Soạn một ca chuyển cho lab coach.
    Input: tóm tắt câu hỏi (str). Output: {"trang_thai": "nhap_cho_gui", "tom_tat"}.
    Có tác động ra ngoài khi gắn Discord (tag lab coach), nên ở đây chỉ tạo bản nháp."""
    return {"trang_thai": "nhap_cho_gui", "tom_tat": tom_tat}
