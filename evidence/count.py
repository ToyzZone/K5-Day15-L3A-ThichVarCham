"""Counts on the assistant channel export. The raw file stays out of the repo (gitignore: evidence/**/raw-*).
Run: python evidence/count.py evidence/discord/raw-2026-11-27.jsonl
The counting rule is in evidence/data-mining.md section 1, written before this file was first run.
Identifiers were renamed to English on the evening of 27/11; the rule and the output did not change."""
import collections
import json
import re
import sys

rows = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8")]


def is_bot(r):
    return (r["a"] or "").startswith("BOT:")


# Denominator: turns where Kute replies to a message from a person
turns = [r for r in rows if is_bot(r) and r["r"] and (r["r"]["a"] or "").startswith("P")]
N = len(turns)


def kind(r):
    t = r["text"] or ""
    if "@Mod" in t:
        return "chuyen_mod"
    if "request timeout" in t:
        return "loi_timeout"
    if not t.strip() and (r["emb"] or "").startswith("Tạo ticket hỗ trợ"):
        return "menu_ticket"
    return "co_tra_loi"


TIME_WORDS = re.compile(r"hôm nay|hôm qua|ngày mai|tối nay|sáng nay|chiều nay|sáng mai|tuần này|tuần sau|bây giờ|hiện tại|mấy giờ|link zoom", re.I)
PRIVATE_ITEMS = re.compile(r"xp|điểm danh|điểm|mã học viên|mssv|nhóm|đội|level|gate|bài nộp|standup|tên hiển thị", re.I)
FIRST_PERSON = re.compile(r"của (mình|tôi|em|tớ)|\b(mình|tôi|em|tớ) (đã|có|bị|được|chưa|vẫn)", re.I)


def pct(x, n):
    return f"{x}/{n} ({100 * x / n:.0f}%)" if n else "0/0"


counts = collections.Counter(kind(r) for r in turns)
print("N lượt Kute trả lời người:", N)
for k in ("co_tra_loi", "chuyen_mod", "menu_ticket", "loi_timeout"):
    print(f"  {k}: {pct(counts[k], N)}")
print("  không tự trả lời được (chuyen_mod + menu_ticket + loi_timeout):", pct(N - counts["co_tra_loi"], N))

# Repeated answers: the same first 60 characters (person codes removed, whitespace collapsed) appear >= 3 times
answered = [r for r in turns if kind(r) == "co_tra_loi"]
key = lambda r: re.sub(r"\s+", " ", re.sub(r"@?P\d+", "", r["text"] or r["emb"] or "")).strip().lower()[:60]
frequency = collections.Counter(key(r) for r in answered)
repeated = sum(v for v in frequency.values() if v >= 3)
print("Câu trả lời lặp (cùng một câu trả lời >= 3 lần):", pct(repeated, len(answered)), "· số câu trả lời khác nhau bị lặp:", sum(1 for v in frequency.values() if v >= 3))

# Questions that depend on when they are asked
question_of = lambda r: r["r"]["t"] or ""
timed = [r for r in turns if TIME_WORDS.search(question_of(r))]
print("Câu hỏi phụ thuộc thời điểm:", pct(len(timed), N), "· trong đó Kute không tự trả lời được:", pct(sum(1 for r in timed if kind(r) != "co_tra_loi"), len(timed)))

# Private-info questions (keyword estimate)
private = [r for r in turns if PRIVATE_ITEMS.search(question_of(r)) and FIRST_PERSON.search(question_of(r))]
print("Câu hỏi thông tin riêng (từ khoá):", pct(len(private), N))

# Extra count (added 19:07 27/11, AFTER seeing the results above): split menu_ticket turns by whether the student asked for a ticket
menu = [r for r in turns if kind(r) == "menu_ticket"]
asked_ticket = sum(1 for r in menu if re.search(r"ticket", question_of(r), re.I))
print("Bổ sung · menu_ticket do học viên xin ticket (tin hỏi có chữ 'ticket'):", pct(asked_ticket, len(menu)))
print("Bổ sung · Kute không trả lời được dù học viên không xin ticket:", pct(counts["chuyen_mod"] + counts["loi_timeout"] + len(menu) - asked_ticket, N))

# Correction (added evening 27/11, after CP2, AFTER reading the chuyen_mod turns): this category mixes two different kinds
mod_only = sum(1 for r in turns if kind(r) == "chuyen_mod" and (r["text"] or "").lstrip().startswith("@Mod"))
print("Đính chính · chỉ gọi Mod, không trả lời (tin bắt đầu bằng @Mod):", pct(mod_only, N))
print("Đính chính · có trả lời rồi nhắc tới Mod:", pct(counts["chuyen_mod"] - mod_only, N))
print("Đính chính · Kute không trả lời được dù học viên không xin ticket:", pct(mod_only + counts["loi_timeout"] + len(menu) - asked_ticket, N))
clarifying = sum(1 for r in turns if kind(r) == "co_tra_loi" and "mô tả rõ hơn" in (r["text"] or ""))
print("Bổ sung · Kute hỏi lại bằng danh sách lựa chọn (tin có 'mô tả rõ hơn'):", pct(clarifying, N))

# Users and frequency (descriptive, added evening 27/11): who asks Kute and how many turns in the collection window
per_asker = collections.Counter(r["r"]["a"] for r in turns)
needed_human = {r["r"]["a"] for r in turns if kind(r) == "chuyen_mod" or (kind(r) == "menu_ticket" and re.search(r"ticket", question_of(r), re.I))}
sizes = sorted(per_asker.values())
print("Người hỏi Kute:", len(sizes), "· trung vị", sizes[len(sizes) // 2], "lượt · nhiều nhất", sizes[-1])
for label, a, b in (("ít (1-2 lượt)", 1, 2), ("vừa (3-6 lượt)", 3, 6), ("nhiều (>=7 lượt)", 7, 10**6)):
    group = [x for x in sizes if a <= x <= b]
    print(f"  {label}: {pct(len(group), len(sizes))} người · {pct(sum(group), N)} lượt · trung bình {sum(group) / len(group):.1f} lượt/người")
print("Người có >=1 lượt kết thúc ở người:", pct(len(needed_human), len(sizes)))
per_day = sorted(collections.Counter(r["t"][:10] for r in turns).values())
print("Lượt mỗi ngày: trung vị", per_day[len(per_day) // 2], "· ít nhất", per_day[0], "· nhiều nhất", per_day[-1], "· số ngày", len(per_day))

if "--vd" in sys.argv:
    for label, subset in (("thoi_diem_khong_tra_loi", [r for r in timed if kind(r) != "co_tra_loi"]), ("rieng", private)):
        print("---", label)
        for r in subset[:12]:
            print(r["id"][-6:], "|", re.sub(r"\s+", " ", question_of(r))[:110], "=>", kind(r))
