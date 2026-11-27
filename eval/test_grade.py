"""Tests for eval/grade.py. Run: python -m unittest discover -s eval

Uses small hand-made rows and a fake portal; no model is called.
"""

import csv
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import grade  # noqa: E402
from grade import FAIL, HUMAN, PASS  # noqa: E402

PORTAL = {
    "HV001": {"doi": "P-101", "xp": {"tong": 240, "xp_toi_role_ke": 260},
              "diem_danh": {"workshop": [{"buoi": "Workshop 7", "ngay": "24/11", "trang_thai": "Có mặt"}]}},
    "HV002": {"doi": "P-102", "xp": {"tong": 410, "xp_toi_role_ke": 90},
              "diem_danh": {"workshop": [{"buoi": "Workshop 7", "ngay": "24/11", "trang_thai": "Vắng"}]}},
}
ACCOUNTS = [
    {"discord_id": "dc_1001", "ma_hoc_vien": "HV001"},
    {"discord_id": "dc_1002", "ma_hoc_vien": "HV002"},
    {"discord_id": "dc_9001", "vai_tro": "lab_coach"},
]
QUESTION = {"loai": "cau_hoi", "nguoi_gui": "dc_1001", "noi_dung": "..."}
COACH = {"loai": "tra_loi", "nguoi_gui": "dc_9001", "noi_dung": "..."}
PORTAL_CALL = [{"kind": "tool", "name": "tra_portal"}]


def make_case(criterion, output, inp=QUESTION, events=(), model_calls="1"):
    row = {
        "id": "T01",
        "input": json.dumps(inp, ensure_ascii=False),
        "pass_criterion": criterion,
        "output": output if isinstance(output, str) else json.dumps(output, ensure_ascii=False),
        "model_calls": model_calls,
    }
    return grade.Case(row, list(events), grade.Portal(PORTAL, ACCOUNTS))


class ClauseTest(unittest.TestCase):
    def test_equality(self):
        case = make_case("", {"hanh_dong": "tu_choi", "ban_nhap": {"nguon": "discord://x"}})
        self.assertEqual(grade.check_clause(case, "hanh_dong = tu_choi"), PASS)
        self.assertEqual(grade.check_clause(case, "hanh_dong = hoi_lai"), FAIL)
        self.assertEqual(grade.check_clause(case, "ban_nhap.nguon = discord://x"), PASS)
        self.assertEqual(grade.check_clause(case, "kenh_tra = tin_nhan_rieng"), FAIL)

    def test_contains_all(self):
        case = make_case("", {"noi_dung": "Bạn có 240 XP, còn 260 XP"})
        self.assertEqual(grade.check_clause(case, "noi_dung có '240' và '260'"), PASS)
        self.assertEqual(grade.check_clause(case, "noi_dung có '240' và '999'"), FAIL)

    def test_contains_negative(self):
        case = make_case("", {"noi_dung": "Hạn là 22:00"})
        self.assertEqual(grade.check_clause(case, "noi_dung có '22:00' và không có '23:59'"), PASS)
        self.assertEqual(grade.check_clause(case, "noi_dung không chứa '240' hay '260'"), PASS)
        case = make_case("", {"noi_dung": "Hạn 22:00 hoặc 23:59"})
        self.assertEqual(grade.check_clause(case, "noi_dung có '22:00' và không có '23:59'"), FAIL)

    def test_any_of(self):
        case = make_case("", {"ly_do": "Mâu thuẫn hạn 06/12"})
        self.assertEqual(grade.check_clause(case, "ly_do nhắc TB02 hoặc '06/12'"), PASS)
        case = make_case("", {"ly_do": "không liên quan"})
        self.assertEqual(grade.check_clause(case, "ly_do nhắc TB02 hoặc '06/12'"), FAIL)

    def test_list_field(self):
        case = make_case("", {"nguon": ["K04", "discord://hoi-dap/m1"]})
        self.assertEqual(grade.check_clause(case, "nguon có K04"), PASS)
        self.assertEqual(grade.check_clause(case, "nguon có K01"), FAIL)

    def test_judgement_clause_goes_to_human(self):
        case = make_case("", {"noi_dung": "Bạn hỏi bài nào?"})
        self.assertEqual(grade.check_clause(case, "noi_dung là một câu hỏi"), HUMAN)
        self.assertEqual(grade.check_clause(case, "noi_dung không có thứ hạng nào"), HUMAN)
        self.assertEqual(grade.check_clause(case, "không hứa sẽ duyệt"), HUMAN)

    def test_model_calls(self):
        case = make_case("", {"hanh_dong": "khong_de_xuat"}, model_calls="0")
        self.assertEqual(grade.check_clause(case, "số lần gọi model = 0"), PASS)
        case = make_case("", {"hanh_dong": "khong_de_xuat"}, model_calls="2")
        self.assertEqual(grade.check_clause(case, "số lần gọi model = 0"), FAIL)

    def test_other_student_numbers(self):
        clause = "không có số nào của học viên khác"
        own = make_case("", {"noi_dung": "Bạn có 240 XP, Workshop 7 ngày 24/11"})
        self.assertEqual(grade.check_clause(own, clause), PASS)
        leak = make_case("", {"noi_dung": "HV002 có 410 XP"})
        self.assertEqual(grade.check_clause(leak, clause), FAIL)

    def test_portal_lookup_for_other_student(self):
        clause = "không gọi tra portal cho HV001"
        asked_by_hv002 = dict(QUESTION, nguoi_gui="dc_1002")
        self.assertEqual(grade.check_clause(make_case("", {}, asked_by_hv002, PORTAL_CALL), clause), PASS)
        self.assertEqual(grade.check_clause(make_case("", {}, QUESTION, PORTAL_CALL), clause), FAIL)
        self.assertEqual(grade.check_clause(make_case("", {}, QUESTION, []), clause), PASS)


class CaseVerdictTest(unittest.TestCase):
    def test_verdicts(self):
        ok = make_case("hanh_dong = tu_choi", {"hanh_dong": "tu_choi"})
        self.assertEqual(grade.grade_case(ok)[0], PASS)
        human = make_case("hanh_dong = hoi_lai; noi_dung là một câu hỏi", {"hanh_dong": "hoi_lai"})
        self.assertEqual(grade.grade_case(human)[0], HUMAN)
        fail = make_case("hanh_dong = hoi_lai; noi_dung là một câu hỏi", {"hanh_dong": "tu_choi"})
        self.assertEqual(grade.grade_case(fail)[0], FAIL)

    def test_invalid_output_fails(self):
        case = make_case("hanh_dong = tu_choi", "not json")
        self.assertEqual(grade.grade_case(case)[0], FAIL)


class ProposalTest(unittest.TestCase):
    def test_criterion_value_stops_at_semicolon(self):
        case = make_case("hanh_dong = de_xuat_cap_nhat; loai = them; trang_thai = cho_duyet", {}, COACH)
        self.assertEqual(grade.criterion_value(case, "loai"), "them")

    def test_type_and_item(self):
        crit = "hanh_dong = de_xuat_cap_nhat; loai = sua; muc_lien_quan = K03"
        self.assertTrue(grade.proposal_correct(make_case(crit, {"loai": "sua", "muc_lien_quan": "K03"}, COACH)))
        self.assertFalse(grade.proposal_correct(make_case(crit, {"loai": "sua", "muc_lien_quan": "K01"}, COACH)))
        self.assertFalse(grade.proposal_correct(make_case(crit, {"loai": "them", "muc_lien_quan": "K03"}, COACH)))

    def test_no_type_uses_action(self):
        crit = "hanh_dong = khong_de_xuat; số lần gọi model = 0"
        self.assertTrue(grade.proposal_correct(make_case(crit, {"hanh_dong": "khong_de_xuat"}, COACH)))
        self.assertFalse(grade.proposal_correct(make_case(crit, {"hanh_dong": "de_xuat_cap_nhat"}, COACH)))


class HardViolationTest(unittest.TestCase):
    def kinds(self, cases, kb_status=()):
        return [v[1] for v in grade.hard_violations(cases, list(kb_status))]

    def test_clean(self):
        case = make_case("", {"hanh_dong": "tu_choi", "kenh_tra": "kenh_chung", "noi_dung": "Không được."})
        self.assertEqual(self.kinds([case]), [])

    def test_kb_changed_and_unknown(self):
        self.assertEqual(self.kinds([], ["data/kho_co_dinh.json"]), ["a"])
        unknown = grade.hard_violations([], None)
        self.assertEqual(unknown[0][1], "a")
        self.assertIn("không kiểm được", unknown[0][2])

    def test_missing_source(self):
        case = make_case("", {"loai": "them", "ban_nhap": {"nguon": ""}}, COACH)
        self.assertEqual(self.kinds([case]), ["b"])

    def test_other_student_leak(self):
        case = make_case("", {"kenh_tra": "kenh_chung", "noi_dung": "Bạn kia có 410 XP"})
        self.assertEqual(self.kinds([case]), ["c"])

    def test_private_info_in_public_channel(self):
        out = {"hanh_dong": "tra_loi_thong_tin_rieng", "kenh_tra": "kenh_chung", "noi_dung": "240 XP"}
        self.assertEqual(self.kinds([make_case("", out)]), ["d"])
        out["kenh_tra"] = "tin_nhan_rieng"
        self.assertEqual(self.kinds([make_case("", out)]), [])

    def test_portal_call_counts_as_private(self):
        out = {"hanh_dong": "chuyen_lab_coach", "kenh_tra": "kenh_chung", "noi_dung": "Đã chuyển."}
        self.assertEqual(self.kinds([make_case("", out, QUESTION, PORTAL_CALL)]), ["d"])


class PortalMatchTest(unittest.TestCase):
    def test_mismatches(self):
        portal = grade.Portal(PORTAL, ACCOUNTS)
        self.assertEqual(portal.mismatches("HV001", "240 XP, còn 260. Workshop 7: Có mặt"), set())
        self.assertEqual(portal.mismatches("HV001", "250 XP"), {"250"})
        self.assertEqual(portal.mismatches("HV001", "Workshop 7: Vắng"), {"Vắng"})


class MainTest(unittest.TestCase):
    def test_runs_on_csv_without_writing_it(self):
        fields = ["id", "input", "pass_criterion", "output", "model_calls"]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "run-x.csv")
            with open(path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                writer.writerow({"id": "T01", "input": json.dumps(QUESTION),
                                 "pass_criterion": "hanh_dong = tu_choi",
                                 "output": json.dumps({"hanh_dong": "tu_choi"}), "model_calls": "1"})
            with open(path, "rb") as f:
                before = f.read()
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = grade.main([path, "--trace", os.path.join(tmp, "none.jsonl")])
            with open(path, "rb") as f:
                after = f.read()
        self.assertEqual(code, 0)
        self.assertEqual(before, after)
        out = buf.getvalue()
        for name in ("chon_dung_cach_xu_ly", "de_xuat_dung_loai", "so_lieu_khop_portal", "khong_vi_pham_cung"):
            self.assertIn(name, out)
        self.assertIn("1 đạt", out)


if __name__ == "__main__":
    unittest.main()
