"""Tests for the timetable path of agent.py. Run: python -m unittest discover -s codebase

The model is a fixed script and tra_tkb is a stub over a made-up timetable, so nothing calls a model, MCP or the API.
"""
import json
import os
import tempfile
import unittest
from datetime import datetime
from unittest import mock

import agent
import tkb
import tools
from test_tkb import session, write

SATURDAY = '2026-11-28T10:00:00+07:00'
GROUP_MEMBER = {'vai_tro': 'hoc_vien', 'ma_hoc_vien': 'unlinked:group'}


class Script:
    """Stands in for call_model and keeps every system prompt it was given."""

    def __init__(self, *replies):
        self.replies, self.systems = list(replies), []

    def __call__(self, system, user):
        self.systems.append(system)
        text = json.dumps(self.replies.pop(0), ensure_ascii=False) if self.replies else ''
        return {'text': text, 'model': 'script', 'tokens_in': 0, 'tokens_out': 0}


class TimetableQuestionTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        write(tmp.name, 'mau.html', {'L2A': [session('2026-11-30', 'LEC 9')], 'L2B': [session('2026-12-01', 'LAB 9', ['P101', 'P102'], 'LAB')]}, 100)
        self.files, self.asked_for = tkb.load(tmp.name), []

    def timetable(self, code=''):
        """Stub for tools.tra_tkb: the asker (HV002) is in class L2B."""
        self.asked_for.append(code)
        return tkb.class_schedule(self.files, code or 'L2B') or {'loi': 'Không có lớp này trong thời khoá biểu.', 'lop_co': tkb.class_codes(self.files)}

    def ask(self, text, *replies, on=True, account=None, when=SATURDAY):
        event = {'loai': 'cau_hoi', 'kenh': 'hoi-dap', 'nguoi_gui': 'dc_1002', 'noi_dung': text,
                 'ngu_canh': {'server_id': '1', 'thoi_diem_cau_hoi': when}}
        model = Script(*replies)
        with mock.patch.dict(os.environ, {'PORTAL_TKB_DIR': 'runtime/tkb' if on else ''}), \
                mock.patch.object(agent, 'call_model', model), mock.patch.object(agent, 'tra_tkb', self.timetable):
            out = json.loads(agent.answer_event(event, account or tools.find_account('dc_1002'))['output'])
        return out, model

    def test_off_the_model_gets_the_unchanged_prompt_and_cannot_reach_the_timetable(self):
        out, model = self.ask('Tuần sau mình học gì?', {'hanh_dong': 'tra_tkb', 'khoang': 'tuan_sau'}, on=False)
        self.assertEqual(model.systems, [agent.SYSTEM])
        self.assertNotIn('tra_tkb', agent.SYSTEM)
        self.assertEqual((out['hanh_dong'], self.asked_for), ('chuyen_lab_coach', []))

    def test_group_members_never_get_the_timetable(self):
        _, model = self.ask('Tuần sau lớp L2A học gì?', {'hanh_dong': 'tra_tkb', 'khoang': 'tuan_sau', 'lop': 'L2A'}, account=GROUP_MEMBER)
        self.assertEqual((model.systems, self.asked_for), ([agent.SYSTEM], []))

    def test_own_class_goes_by_direct_message_with_dates_written_by_code(self):
        out, model = self.ask('Tuần sau mình học gì?', {'hanh_dong': 'tra_tkb', 'khoang': 'tuan_sau'}, {'hanh_dong': 'tra_loi_tu_tkb'})
        self.assertIn('tra_tkb', model.systems[0])
        self.assertEqual((out['hanh_dong'], out['kenh_tra'], out['nguon'], self.asked_for), ('tra_loi_tu_tkb', 'tin_nhan_rieng', ['mau.html'], ['']))
        self.assertIn('Thứ 3 01/12, 09:00–13:00: LAB 9 (Thực hành), một trong các phòng P101, P102', out['noi_dung'])

    def test_a_named_class_is_answered_in_the_channel(self):
        out, _ = self.ask('Tuần sau lớp l2a học gì?', {'hanh_dong': 'tra_tkb', 'khoang': 'tuan_sau', 'lop': 'l2a'}, {'hanh_dong': 'tra_loi_tu_tkb'})
        self.assertEqual((out['kenh_tra'], self.asked_for), ('kenh_chung', ['L2A']))
        self.assertIn('Thứ 2 30/11, 09:00–13:00: LEC 9 (Lý thuyết), phòng P101', out['noi_dung'])

    def test_the_window_is_counted_from_the_question_time(self):
        out, _ = self.ask('Hôm nay lớp L2A học gì?', {'hanh_dong': 'tra_tkb', 'khoang': 'hom_nay', 'lop': 'L2A'}, {'hanh_dong': 'tra_loi_tu_tkb'},
                          when='2026-11-30T07:00:00+07:00')
        self.assertIn('vào Thứ 2 30/11', out['noi_dung'])

    def test_no_basis_goes_to_a_lab_coach_even_if_the_model_wants_to_answer(self):
        out, _ = self.ask('Tuần này lớp L2A học gì?', {'hanh_dong': 'tra_tkb', 'khoang': 'tuan_nay', 'lop': 'L2A'}, {'hanh_dong': 'tra_loi_tu_tkb'},
                          when='2027-01-10T08:00:00+07:00')
        self.assertEqual(out['hanh_dong'], 'chuyen_lab_coach')
        self.assertNotRegex(out['noi_dung'], r'\d')

    def test_unknown_class_is_asked_back_by_code(self):
        out, model = self.ask('Lớp L9Z mai học phòng nào?', {'hanh_dong': 'tra_tkb', 'khoang': 'ngay_mai', 'lop': 'L9Z'})
        self.assertEqual((out['hanh_dong'], out['noi_dung'], len(model.systems)),
                         ('hoi_lai', 'Thời khoá biểu hiện có các lớp: L2A, L2B. Bạn hỏi lớp nào?', 1))

    def test_numbers_written_by_the_model_after_a_timetable_lookup_are_blocked(self):
        out, _ = self.ask('Tuần sau mình học gì?', {'hanh_dong': 'tra_tkb', 'khoang': 'tuan_sau'},
                          {'hanh_dong': 'tu_choi', 'noi_dung': 'Bạn học phòng P999 lúc 08:00', 'ly_do_tu_choi': 'ngoai_pham_vi'})
        self.assertEqual(out['hanh_dong'], 'chuyen_lab_coach')
        self.assertNotIn('P999', out['noi_dung'])


class AskedAtTests(unittest.TestCase):
    def test_question_time_wins_and_the_clock_is_the_fallback(self):
        asked = agent._asked_at({'ngu_canh': {'thoi_diem_cau_hoi': '2026-11-28T03:30:00+00:00'}})
        self.assertEqual(asked.isoformat(), '2026-11-28T10:30:00+07:00')
        now = agent._asked_at({})
        self.assertEqual(now.utcoffset(), agent.VN_TZ.utcoffset(None))
        self.assertLess(abs((datetime.now(agent.VN_TZ) - now).total_seconds()), 5)


if __name__ == '__main__':
    unittest.main()
