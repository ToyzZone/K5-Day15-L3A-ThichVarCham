"""Checks for make_label_lots.py and merge_labels.py. Run: python -m unittest evidence/test_label_tools.py"""
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))

import make_label_lots as lots  # noqa: E402
import merge_labels as merge  # noqa: E402


def bot(mid, text, asker="P1", quoted="hỏi gì đó", emb=""):
    return {"id": mid, "t": "2026-11-14T06:10:00.000Z", "a": "BOT:Trợ lý Kute", "r": {"a": asker, "t": quoted},
            "text": text, "emb": emb}


class LotTests(unittest.TestCase):
    def test_pool_keeps_only_answers_with_content(self):
        rows = [
            {"id": "100000001", "t": "2026-11-14T06:09:00.000Z", "a": "P1", "r": None, "text": "hỏi gì đó dài hơn", "emb": ""},
            bot("200000001", "Nộp trước 10:00 nhé @P7."),
            bot("200000002", "@Mod Mình chưa đủ thông tin."),
            bot("200000003", "Xin lỗi, request timeout. Vui lòng thử lại."),
            bot("200000004", "", emb="Tạo ticket hỗ trợ"),
            bot("200000005", "Bạn muốn hỏi gì? Hoặc bạn mô tả rõ hơn giúp mình nhé!"),
        ]
        pool = lots.build_pool(rows)
        self.assertEqual([item["id"] for item in pool], ["00000001"])
        self.assertEqual(pool[0]["question"], "hỏi gì đó dài hơn")  # full question, not the 120-char preview
        self.assertEqual(pool[0]["asked_at"], "14/11/2026 13:10")  # shown in Vietnam time
        self.assertNotIn("P7", pool[0]["answer"])  # person codes are hidden from labellers

    def test_deal_shares_overlap_and_covers_pool_once(self):
        pool = [{"id": str(i)} for i in range(50)]
        dealt = lots.deal(pool, seed=1, lots=4, overlap=6)
        shared = [item["id"] for item in dealt[0][:6]]
        for lot in dealt:
            self.assertEqual([item["id"] for item in lot[:6]], shared)
        rest = [item["id"] for lot in dealt for item in lot[6:]]
        self.assertEqual(len(rest), len(set(rest)))
        self.assertEqual(set(rest) | set(shared), {str(i) for i in range(50)})
        self.assertEqual(lots.deal(pool, seed=1, lots=4, overlap=6), dealt)  # same seed, same lots

    def test_default_split_is_two_lots_sharing_the_overlap(self):
        pool = [{"id": str(i)} for i in range(lots.OVERLAP + 58)]
        first, second = lots.deal(pool)
        self.assertEqual(first[:lots.OVERLAP], second[:lots.OVERLAP])
        self.assertEqual((len(first), len(second)), (lots.OVERLAP + 29, lots.OVERLAP + 29))


class MergeTests(unittest.TestCase):
    def test_majority_agreement_and_ties(self):
        exports = [
            {"lot": 1, "labeler": "a", "labels": [{"id": "x", "label": "dung"}, {"id": "y", "label": "sai"}, {"id": "z", "label": "dung"}]},
            {"lot": 2, "labeler": "b", "labels": [{"id": "x", "label": "dung"}, {"id": "y", "label": "da_cu"}, {"id": "w", "label": "bogus"}]},
        ]
        summary = merge.summarise(merge.collect(exports))
        self.assertEqual(summary["items"], 3)  # the invalid label is dropped
        self.assertEqual(summary["final"]["dung"], 2)
        self.assertEqual(summary["final"]["khong_chac"], 1)  # y is a tie
        self.assertEqual((summary["shared"], summary["unanimous"]), (2, 1))
        self.assertIn("| Đúng | 2/3 | 67% |", merge.to_markdown(summary))


class ToolContractTests(unittest.TestCase):
    """label-tool.html writes the files merge_labels.py reads."""

    def setUp(self):
        with open(os.path.join(os.path.dirname(__file__), "label-tool.html"), encoding="utf-8") as f:
            self.html = f.read()

    def test_tool_offers_exactly_the_labels_merge_counts(self):
        self.assertEqual(re.findall(r'\{ key: "(\w+)"', self.html), merge.LABELS)

    def test_exported_label_files_stay_out_of_git(self):
        self.assertIn("link.download = `raw-nhan-lo-", self.html)  # .gitignore: evidence/**/raw-*


if __name__ == "__main__":
    unittest.main()
