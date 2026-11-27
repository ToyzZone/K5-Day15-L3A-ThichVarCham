"""Đếm trên dữ liệu kênh hỏi trợ lý. Bản thô để ngoài repo (gitignore: evidence/**/raw-*).
Chạy: python evidence/count.py evidence/discord/raw-2026-11-27.jsonl
Luật đếm ở evidence/data-mining.md mục 1, viết trước khi chạy file này."""
import collections
import json
import re
import sys

rows = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8")]


def la_bot(r):
    return (r["a"] or "").startswith("BOT:")


# Mẫu số: lượt Kute trả lời (reply) một tin của người
luot = [r for r in rows if la_bot(r) and r["r"] and (r["r"]["a"] or "").startswith("P")]
N = len(luot)


def loai(r):
    t = r["text"] or ""
    if "@Mod" in t:
        return "chuyen_mod"
    if "request timeout" in t:
        return "loi_timeout"
    if not t.strip() and (r["emb"] or "").startswith("Tạo ticket hỗ trợ"):
        return "menu_ticket"
    return "co_tra_loi"


THOI_DIEM = re.compile(r"hôm nay|hôm qua|ngày mai|tối nay|sáng nay|chiều nay|sáng mai|tuần này|tuần sau|bây giờ|hiện tại|mấy giờ|link zoom", re.I)
MUC_RIENG = re.compile(r"xp|điểm danh|điểm|mã học viên|mssv|nhóm|đội|level|gate|bài nộp|standup|tên hiển thị", re.I)
NGOI_1 = re.compile(r"của (mình|tôi|em|tớ)|\b(mình|tôi|em|tớ) (đã|có|bị|được|chưa|vẫn)", re.I)


def pct(x, n):
    return f"{x}/{n} ({100 * x / n:.0f}%)" if n else "0/0"


dem = collections.Counter(loai(r) for r in luot)
print("N lượt Kute trả lời người:", N)
for k in ("co_tra_loi", "chuyen_mod", "menu_ticket", "loi_timeout"):
    print(f"  {k}: {pct(dem[k], N)}")
print("  không tự trả lời được (chuyen_mod + menu_ticket + loi_timeout):", pct(N - dem["co_tra_loi"], N))

# Câu trả lời lặp: cùng 60 ký tự đầu (bỏ mã người, gộp khoảng trắng) xuất hiện >= 3 lần
co = [r for r in luot if loai(r) == "co_tra_loi"]
khoa = lambda r: re.sub(r"\s+", " ", re.sub(r"@?P\d+", "", r["text"] or r["emb"] or "")).strip().lower()[:60]
tan = collections.Counter(khoa(r) for r in co)
lap = sum(v for v in tan.values() if v >= 3)
print("Câu trả lời lặp (cùng một câu trả lời >= 3 lần):", pct(lap, len(co)), "· số câu trả lời khác nhau bị lặp:", sum(1 for v in tan.values() if v >= 3))

# Câu hỏi phụ thuộc thời điểm
hoi = lambda r: r["r"]["t"] or ""
td = [r for r in luot if THOI_DIEM.search(hoi(r))]
print("Câu hỏi phụ thuộc thời điểm:", pct(len(td), N), "· trong đó Kute không tự trả lời được:", pct(sum(1 for r in td if loai(r) != "co_tra_loi"), len(td)))

# Câu hỏi thông tin riêng (ước lượng bằng từ khoá)
rieng = [r for r in luot if MUC_RIENG.search(hoi(r)) and NGOI_1.search(hoi(r))]
print("Câu hỏi thông tin riêng (từ khoá):", pct(len(rieng), N))

# Đếm bổ sung (thêm 19:07 27/11, SAU khi đã xem kết quả ở trên): tách lượt menu_ticket theo việc học viên có xin ticket không
menu = [r for r in luot if loai(r) == "menu_ticket"]
xin = sum(1 for r in menu if re.search(r"ticket", hoi(r), re.I))
print("Bổ sung · menu_ticket do học viên xin ticket (tin hỏi có chữ 'ticket'):", pct(xin, len(menu)))
print("Bổ sung · Kute không trả lời được dù học viên không xin ticket:", pct(dem["chuyen_mod"] + dem["loi_timeout"] + len(menu) - xin, N))

# Đính chính (thêm tối 27/11, sau CP2, SAU khi đọc nội dung các lượt chuyen_mod): loại này gộp hai kiểu khác nhau
chi_goi = sum(1 for r in luot if loai(r) == "chuyen_mod" and (r["text"] or "").lstrip().startswith("@Mod"))
print("Đính chính · chỉ gọi Mod, không trả lời (tin bắt đầu bằng @Mod):", pct(chi_goi, N))
print("Đính chính · có trả lời rồi nhắc tới Mod:", pct(dem["chuyen_mod"] - chi_goi, N))
print("Đính chính · Kute không trả lời được dù học viên không xin ticket:", pct(chi_goi + dem["loi_timeout"] + len(menu) - xin, N))
hoi_lai = sum(1 for r in luot if loai(r) == "co_tra_loi" and "mô tả rõ hơn" in (r["text"] or ""))
print("Bổ sung · Kute hỏi lại bằng danh sách lựa chọn (tin có 'mô tả rõ hơn'):", pct(hoi_lai, N))

if "--vd" in sys.argv:
    for ten, tap in (("thoi_diem_khong_tra_loi", [r for r in td if loai(r) != "co_tra_loi"]), ("rieng", rieng)):
        print("---", ten)
        for r in tap[:12]:
            print(r["id"][-6:], "|", re.sub(r"\s+", " ", hoi(r))[:110], "=>", loai(r))
