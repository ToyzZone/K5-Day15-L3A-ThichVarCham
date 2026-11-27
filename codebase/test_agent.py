"""Tests for agent.py. Run: python -m unittest discover -s codebase

The model is always replaced by a fixed script, so no test calls a real API even when .env has a key.
"""
import json
import os
import pathlib
import unittest
from unittest import mock

import agent
import tools

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
RUNTIME_KB = tools.RUNTIME_KB
COACH = {"vai_tro": "lab_coach"}
DEADLINE_SCOPE = {"loai_cau_hoi": "deadline_bai_tap", "lop": "L3A", "bai_tap": "Lab15", "ngay": "2026-11-27"}


def question(sender, text, channel="hoi-dap"):
    return json.dumps({"loai": "cau_hoi", "kenh": channel, "nguoi_gui": sender, "noi_dung": text})


def coach_reply(question_text, text, link="discord://m1"):
    event = {"loai": "tra_loi", "kenh": "hoi-dap", "nguoi_gui": "dc_9001", "cau_hoi": question_text, "noi_dung": text}
    if link:
        event["link"] = link
    return json.dumps(event)


def kb_files():
    return [pathlib.Path(DATA, name).read_text(encoding="utf-8") for name in ("kho_co_dinh.json", "kho_theo_khoa.json")]


class ScriptedModel:
    """Stands in for call_model: returns the given replies in order, then an empty (unparseable) reply."""

    def __init__(self, *replies):
        self.replies, self.calls = list(replies), 0

    def __call__(self, system, user):
        self.calls += 1
        text = json.dumps(self.replies.pop(0), ensure_ascii=False) if self.replies else ""
        return {"text": text, "model": "script", "tokens_in": 0, "tokens_out": 0}


def run(text, *replies):
    model = ScriptedModel(*replies)
    with mock.patch.object(agent, "call_model", model):
        return json.loads(agent.answer(text)["output"]), model.calls


def run_event(event, account, kb, *replies):
    """Run the Discord path: a verified account and a runtime knowledge base."""
    model, token = ScriptedModel(*replies), RUNTIME_KB.set(kb)
    try:
        with mock.patch.object(agent, "call_model", model):
            return json.loads(agent.answer_event(event, account)["output"]), model.calls
    finally:
        RUNTIME_KB.reset(token)


class QuestionTests(unittest.TestCase):
    def test_unknown_sender_is_refused_without_calling_the_model(self):
        out, calls = run(question("dc_0000", "XP của mình?"))
        self.assertEqual((out["hanh_dong"], calls), ("tu_choi", 0))

    def test_private_question_in_public_channel_goes_to_dm_with_own_numbers(self):
        out, _ = run(question("dc_1002", "XP của mình?"), {"hanh_dong": "tra_portal", "muc": "xp"}, {"hanh_dong": "tra_loi_thong_tin_rieng"})
        self.assertEqual(out["kenh_tra"], "tin_nhan_rieng")
        self.assertIn("410", out["noi_dung"])
        self.assertNotIn("240", out["noi_dung"])

    def test_model_cannot_look_up_another_student(self):
        out, _ = run(question("dc_1002", "XP của HV001?"), {"hanh_dong": "tra_portal", "muc": "HV001"}, {"hanh_dong": "tra_loi_thong_tin_rieng"})
        self.assertNotIn("240", out["noi_dung"])
        self.assertNotIn("260", out["noi_dung"])

    def test_numbers_written_by_the_model_after_a_portal_lookup_are_blocked(self):
        out, _ = run(question("dc_1002", "XP?"), {"hanh_dong": "tra_portal", "muc": "xp"}, {"hanh_dong": "tu_choi", "noi_dung": "Bạn có 999 XP", "ly_do_tu_choi": "ngoai_pham_vi"})
        self.assertNotIn("999", out["noi_dung"])
        self.assertEqual((out["hanh_dong"], out["kenh_tra"]), ("chuyen_lab_coach", "tin_nhan_rieng"))

    def test_knowledge_answer_is_copied_from_the_entry_not_the_model(self):
        out, _ = run(question("dc_1001", "XP được tính thế nào ạ?"), {"hanh_dong": "tra_kho", "truy_van": "XP được tính thế nào"},
                     {"hanh_dong": "tra_loi_tu_kho", "muc_kho": "K04", "noi_dung": "bịa"})
        self.assertEqual(out["hanh_dong"], "tra_loi_tu_kho")
        self.assertNotIn("bịa", out["noi_dung"])
        self.assertIn("K04", out["nguon"])

    def test_unparseable_model_reply_hands_the_question_to_a_lab_coach_ticket(self):
        out, _ = run(question("dc_1001", "gì đó"))
        self.assertEqual(out["hanh_dong"], "chuyen_lab_coach")
        self.assertEqual(out["ticket"]["trang_thai"], "cho_hoc_vien_xac_nhan")

    def test_refusal_without_an_allowed_reason_goes_to_a_lab_coach(self):
        out, _ = run(question("dc_1001", "Hạn nộp lab?"), {"hanh_dong": "tu_choi", "noi_dung": "Không hỗ trợ."})
        self.assertEqual(out["hanh_dong"], "chuyen_lab_coach")

    def test_runtime_entry_matching_the_question_is_returned_without_the_model(self):
        event = {"loai": "cau_hoi", "kenh": "hoi-dap", "nguoi_gui": "1", "noi_dung": "XP được tính thế nào?", "ngu_canh": {"server_id": "1"}}
        out, calls = run_event(event, {"vai_tro": "hoc_vien", "ma_hoc_vien": "unlinked:1"}, tools.seed_knowledge())
        self.assertEqual((out["hanh_dong"], calls), ("tra_loi_tu_kho", 0))
        self.assertIn("K04", out["nguon"])


class ProposalTests(unittest.TestCase):
    def test_sender_without_the_coach_role_gets_no_proposal_and_no_model_call(self):
        event = json.loads(coach_reply("a", "ghi vào kho", link="x"))
        event["nguoi_gui"] = "dc_1003"  # display name "Lab Coach", role learner
        out, calls = run(json.dumps(event))
        self.assertEqual((out["hanh_dong"], calls), ("khong_de_xuat", 0))

    def test_proposal_waits_for_review_and_cites_the_coach_message(self):
        before = kb_files()
        out, _ = run(coach_reply("nộp trễ standup có XP không", "không"), {"loai": "them", "ly_do": "ok", "cau_hoi": "q", "tra_loi": "a"})
        self.assertEqual(out["trang_thai"], "cho_duyet")
        self.assertEqual((out["ban_nhap"]["nguon"], out["ban_nhap"]["bang"]), ("discord://m1", "theo_khoa"))
        self.assertEqual(kb_files(), before)

    def test_unparseable_model_reply_becomes_a_warning(self):
        out, _ = run(coach_reply("a", "b", link="l"))
        self.assertEqual(out["loai"], "canh_bao")

    def test_reply_without_a_link_is_not_a_draft(self):
        out, _ = run(coach_reply("a", "b", link=None), {"loai": "them", "ly_do": "ok"})
        self.assertEqual(out["loai"], "canh_bao")
        self.assertIsNone(out["ban_nhap"])

    def test_editing_a_fixed_entry_drafts_a_course_entry_over_it(self):
        before = kb_files()
        out, _ = run(coach_reply("Nộp daily standup ở đâu ạ?", "Nộp ở tab Daily standup", link="discord://m2"),
                     {"loai": "sua", "muc_lien_quan": "K03", "ly_do": "đổi nơi nộp", "cau_hoi": "q", "tra_loi": "a"})
        self.assertEqual(out["loai"], "sua")
        self.assertEqual(out["ban_nhap"], {"cau_hoi": "q", "tra_loi": "a", "nguon": "discord://m2", "bang": "theo_khoa", "ghi_de": "K03"})
        self.assertEqual(kb_files(), before)

    def discord_reply(self, scope):
        kb = tools.seed_knowledge() + [{"ma": "D1", "bang": "theo_khoa", "cau_hoi": "Hạn nộp Lab15 lớp L3A ngày 27/11?", "tra_loi": "22:00",
                                 "nguon": "discord://m0", "trang_thai": "hieu_luc",
                                 "pham_vi": dict(DEADLINE_SCOPE, gia_tri="2026-11-27T22:00:00+07:00", server_id="1")}]
        event = {"loai": "tra_loi", "kenh": "hoi-dap", "nguoi_gui": "c", "cau_hoi": "Hạn nộp lab hôm nay?", "noi_dung": "23:00 nhé",
                 "link": "discord://m9", "ngu_canh": {"server_id": "1", "thoi_diem_cau_hoi": "2026-11-27T10:00:00+07:00"}}
        out, _ = run_event(event, COACH, kb, {"loai": "them", "ly_do": "x", "cau_hoi": "q", "tra_loi": "a", "pham_vi": scope})
        return out

    def test_reply_in_the_scope_of_a_live_entry_becomes_an_edit_of_it(self):
        out = self.discord_reply(dict(DEADLINE_SCOPE, gia_tri="2026-11-27T23:00:00+07:00"))
        self.assertEqual((out["loai"], out["muc_lien_quan"], out["ban_nhap"]["ghi_de"]), ("sua", "D1", "D1"))
        self.assertEqual(out["ban_nhap"]["pham_vi"]["gia_tri"], "2026-11-27T23:00:00+07:00")

    def test_deadline_without_a_time_asks_the_coach_to_complete_it(self):
        out = self.discord_reply(dict(DEADLINE_SCOPE))
        self.assertEqual(out["loai"], "canh_bao")
        self.assertTrue(out["can_chinh_sua"])
        self.assertFalse(out["can_duyet_ghi_de"])


if __name__ == "__main__":
    unittest.main()
