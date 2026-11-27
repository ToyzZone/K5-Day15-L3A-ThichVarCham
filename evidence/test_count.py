"""Checks count.py on a small made-up export. Run: python -m unittest discover -s evidence"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

COUNT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "count.py")

# (asker, question, Kute's text, Kute's embed). P1 asks once, P2 three times, P3 seven times.
TURNS = ([("P1", "cho mình ticket", "", "Tạo ticket hỗ trợ")]
         + [("P2", "hạn nộp lab hôm nay", "@Mod mình chưa đủ thông tin", ""),
            ("P2", "xp của mình", "Xin lỗi, request timeout. Vui lòng thử lại.", ""),
            ("P2", "lab nộp ở đâu", "Nộp ở portal, cần thêm thì hỏi @Mod", "")]
         + [("P3", "XP tính sao", "XP tính theo bài nộp", "")] * 7)


def export():
    rows = []
    for i, (asker, question, text, emb) in enumerate(TURNS):
        when = "2026-11-%02dT06:00:00.000Z" % (14 + i % 2)
        rows.append({"id": "q%d" % i, "t": when, "a": asker, "r": None, "text": question, "emb": ""})
        rows.append({"id": "b%d" % i, "t": when, "a": "BOT:Trợ lý Kute", "r": {"a": asker, "t": question}, "text": text, "emb": emb})
    return rows


class CountTests(unittest.TestCase):
    def test_counts_on_a_known_export(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "raw-test.jsonl")
            with open(path, "w", encoding="utf-8") as f:
                f.writelines(json.dumps(row, ensure_ascii=False) + "\n" for row in export())
            out = subprocess.run([sys.executable, COUNT, path], capture_output=True, check=True,
                                 env=dict(os.environ, PYTHONIOENCODING="utf-8")).stdout.decode("utf-8").splitlines()
        for line in ("N lượt Kute trả lời người: 11",
                     "  co_tra_loi: 7/11 (64%)",
                     "  chuyen_mod: 2/11 (18%)",
                     "  menu_ticket: 1/11 (9%)",
                     "  loi_timeout: 1/11 (9%)",
                     "Bổ sung · menu_ticket do học viên xin ticket (tin hỏi có chữ 'ticket'): 1/1 (100%)",
                     "Đính chính · chỉ gọi Mod, không trả lời (tin bắt đầu bằng @Mod): 1/11 (9%)",
                     "Người hỏi Kute: 3 · trung vị 3 lượt · nhiều nhất 7",
                     "Người có >=1 lượt kết thúc ở người: 2/3 (67%)"):
            self.assertIn(line, out)


if __name__ == "__main__":
    unittest.main()
