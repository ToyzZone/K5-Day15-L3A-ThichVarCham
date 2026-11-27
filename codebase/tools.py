"""Công cụ của trợ lý Discord — khớp bảng công cụ ở spec.md §4.

Mỗi công cụ là một hàm có @tool. Dữ liệu đọc từ data/ (mô tả ở data/DATA_CARD.md).
Không công cụ nào ghi vào kho kiến thức: mục kho chỉ có hiệu lực sau khi lab coach duyệt.

Kho kiến thức có HAI BẢNG:
    data/kho_co_dinh.json   bảng cố định: thông tin giữ nguyên qua các khoá. Lab coach không sửa bảng này.
    data/kho_theo_khoa.json bảng theo khoá: thông tin riêng của khoá đang chạy. Mọi đề xuất được duyệt vào đây.
Khi hai bảng mâu thuẫn, bảng theo khoá thắng: mục theo khoá có "ghi_de" sẽ che mục bị ghi đè.
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


def _kho():
    """Gộp hai bảng. Thứ tự ưu tiên do code quyết: mục theo khoá che mục mà nó ghi đè."""
    con = lambda ten: [m for m in _doc(ten) if m["trang_thai"] == "hieu_luc"]
    theo_khoa, co_dinh = con("kho_theo_khoa.json"), con("kho_co_dinh.json")
    bi_che = {m.get("ghi_de") for m in theo_khoa}
    return ([dict(m, bang="theo_khoa") for m in theo_khoa if m["ma"] not in bi_che]
            + [dict(m, bang="co_dinh") for m in co_dinh if m["ma"] not in bi_che])


@tool
def tra_kho_kien_thuc(cau_hoi: str) -> list:
    """Tra kho kiến thức, gồm bảng cố định và bảng theo khoá (chỉ mục đang hiệu lực).
    Input: câu hỏi (str). Output: tối đa 3 mục {"ma", "bang", "cau_hoi", "tra_loi", "nguon"}; [] nếu không có.
    Mục cố định đã bị mục theo khoá ghi đè thì không được trả về. Không tác động ra ngoài."""
    muc = _kho()
    return [{k: m[k] for k in ("ma", "bang", "cau_hoi", "tra_loi", "nguon")}
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
def tao_ticket(tom_tat: str) -> dict:
    """Soạn một ticket Discord gửi lab coach (cách chuyển câu hỏi cho người).
    Input: tóm tắt câu hỏi (str). Output: {"trang_thai": "cho_hoc_vien_xac_nhan", "tom_tat"}.
    Có tác động ra ngoài (mở ticket, lab coach nhận thông báo), nên công cụ chỉ SOẠN:
    ticket chỉ được tạo thật khi học viên bấm xác nhận."""
    return {"trang_thai": "cho_hoc_vien_xac_nhan", "tom_tat": tom_tat}
