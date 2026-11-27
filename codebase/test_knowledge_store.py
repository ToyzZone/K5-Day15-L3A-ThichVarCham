"""Tests for knowledge_store.py. Run: python -m unittest discover -s codebase"""
import os
import tempfile
import unittest

from knowledge_store import KnowledgeStore

FIXED = {"ma": "K05", "bang": "co_dinh", "cau_hoi": "Hạn nộp lab?", "tra_loi": "23:59", "nguon": "l0", "trang_thai": "hieu_luc"}
DRAFT = {"cau_hoi": "Hạn nộp lab?", "tra_loi": "22:00", "nguon": "discord://m1", "bang": "theo_khoa", "ghi_de": None}


def proposal(kind, **extra):
    return dict({"loai": kind, "ly_do": "lý do", "muc_lien_quan": None, "ban_nhap": dict(DRAFT)}, **extra)


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "kb.db")
        self.store = KnowledgeStore(self.path, [FIXED])

    def tearDown(self):
        self.store.close()
        self.dir.cleanup()

    def learned(self):
        return [m for m in self.store.knowledge() if m["ma"] != "K05"]

    def test_same_source_message_is_proposed_once(self):
        self.assertEqual(self.store.propose("m1", "2026-11-27T10:00:00+00:00", proposal("them")), 1)
        self.assertIsNone(self.store.propose("m1", "2026-11-27T10:00:00+00:00", proposal("them")))

    def test_approved_proposal_becomes_a_live_course_entry_and_survives_reopen(self):
        pid = self.store.propose("m1", "2026-11-27T10:00:00+00:00", proposal("them"))
        self.store.decide(pid, "coach", approve=True)
        self.store.close()
        self.store = KnowledgeStore(self.path, [FIXED])
        [new] = self.learned()
        self.assertEqual(set(new), {"cau_hoi", "tra_loi", "nguon", "bang", "ghi_de", "ma", "trang_thai", "nguoi_duyet", "ngay_duyet",
                                    "source_created_at", "duyet_ghi_de", "canh_bao_khi_duyet"})
        self.assertEqual((new["ma"], new["bang"], new["trang_thai"], new["nguoi_duyet"]), ("D1", "theo_khoa", "hieu_luc", "coach"))
        with self.assertRaises(ValueError):
            self.store.decide(pid, "coach", approve=True)  # already decided

    def test_edit_of_a_fixed_entry_leaves_it_in_place(self):
        pid = self.store.propose("m1", "2026-11-27T10:00:00+00:00", proposal("sua", muc_lien_quan="K05"))
        self.store.decide(pid, "coach", approve=True)
        fixed = next(m for m in self.store.knowledge() if m["ma"] == "K05")
        self.assertEqual(fixed["trang_thai"], "hieu_luc")
        self.assertEqual(self.learned()[0]["ghi_de"], "K05")

    def test_warning_enters_the_kb_only_by_override(self):
        pid = self.store.propose("m1", "2026-11-27T10:00:00+00:00", proposal("canh_bao", can_duyet_ghi_de=True))
        with self.assertRaises(ValueError):
            self.store.decide(pid, "coach", approve=True)
        self.store.decide(pid, "coach", approve=True, override=True)
        [new] = self.learned()
        self.assertEqual((new["duyet_ghi_de"], new["canh_bao_khi_duyet"]), (True, "lý do"))

    def test_rejected_proposal_changes_nothing(self):
        pid = self.store.propose("m1", "2026-11-27T10:00:00+00:00", proposal("them"))
        self.store.decide(pid, "coach", approve=False)
        self.assertEqual(self.learned(), [])

    def test_revise_needs_a_complete_draft_and_unlocks_override(self):
        body = proposal("canh_bao", can_chinh_sua=True)
        pid = self.store.propose("m1", "2026-11-27T10:00:00+00:00", body)
        with self.assertRaises(ValueError):
            self.store.revise(pid, dict(DRAFT, nguon=""), "coach", body)
        revised = self.store.revise(pid, dict(DRAFT, pham_vi={"loai_cau_hoi": "khac", "server_id": "1"}), "coach", body)
        self.assertEqual((revised["can_chinh_sua"], revised["can_duyet_ghi_de"], revised["nguoi_chinh_sua"]), (False, True, "coach"))


if __name__ == "__main__":
    unittest.main()
