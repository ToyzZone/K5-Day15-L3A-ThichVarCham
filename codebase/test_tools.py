"""Tests for tools.py. Run: python -m unittest discover -s codebase"""
import unittest

import tools
import tracing


def entry(code, table, status="hieu_luc", overrides=None):
    return {"ma": code, "bang": table, "trang_thai": status, "ghi_de": overrides, "nguon": "l",
            "cau_hoi": "Hạn nộp lab là mấy giờ?", "tra_loi": "Hạn nộp lab " + code}


class ToolTests(unittest.TestCase):
    def test_tools_keep_the_names_in_spec_and_metric(self):
        # The trace records tool names, and the locked metric looks for tra_portal by name.
        self.assertLessEqual({"tra_kho_kien_thuc", "tra_thong_bao", "tra_portal", "tao_ticket"}, set(tracing.TOOLS))

    def test_course_entry_hides_the_fixed_entry_it_overrides(self):
        codes = [m["ma"] for m in tools.tra_kho_kien_thuc("Hạn nộp lab là mấy giờ?")]
        self.assertIn("T01", codes)
        self.assertNotIn("K05", codes)

    def test_runtime_kb_drops_stale_and_overridden_entries(self):
        token = tools.RUNTIME_KB.set([entry("K05", "co_dinh"), entry("D1", "theo_khoa", status="loi_thoi"),
                                       entry("D2", "theo_khoa", overrides="K05")])
        try:
            self.assertEqual([m["ma"] for m in tools.tra_kho_kien_thuc("Hạn nộp lab là mấy giờ?")], ["D2"])
        finally:
            tools.RUNTIME_KB.reset(token)

    def test_portal_only_reads_the_current_student(self):
        self.assertIn("loi", tools.tra_portal("xp"))  # nobody is asking
        token = tools.ASKER_ID.set("HV002")
        try:
            self.assertEqual(tools.tra_portal("xp")["du_lieu"]["tong"], 410)
            self.assertIn("loi", tools.tra_portal("HV001"))
        finally:
            tools.ASKER_ID.reset(token)

    def test_account_lookup(self):
        self.assertEqual(tools.find_account("dc_9001")["vai_tro"], "lab_coach")
        self.assertIsNone(tools.find_account("dc_0000"))

    def test_announcement_search_and_ticket_draft(self):
        self.assertLessEqual(len(tools.tra_thong_bao("hạn nộp lab")), 3)
        self.assertEqual(tools.tao_ticket("x"), {"trang_thai": "cho_hoc_vien_xac_nhan", "tom_tat": "x"})


if __name__ == "__main__":
    unittest.main()
