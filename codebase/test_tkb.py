"""Tests for tkb.py. Run: python -m unittest discover -s codebase

Every timetable here is made up (classes, rooms, session names). The page has the same shape as the real files,
including a per-student table that the reader must never touch.
"""
import json
import os
import pathlib
import tempfile
import unittest
from datetime import date, datetime

import tkb

DECOY = 'HV999'


def session(day, name='LEC 1', rooms=('P101',), kind='LEC', time=('09:00', '13:00')):
    return {'d': day, 'slot': 'Sáng', 'kind': kind, 'name': name, 'rooms': list(rooms), 'time': list(time)}


def page(groups):
    """A fake timetable page: class schedule, kind labels, and a decoy student table."""
    body = {code: {'label': code, 'level': 'Lớp mẫu', 'items': items, 'size': '3 học viên'} for code, items in groups.items()}
    return ('<!doctype html><html><head><title>Thời khóa biểu mẫu</title></head><body><script>\n'
            "const AM=['09:00','13:00'];\nconst GROUPS = %s;\nconst STU={\"%s\":[\"L2A\",\"P101\"]};\n"
            "const KIND={LEC:'Lý thuyết',LAB:'Thực hành'};\n</script></body></html>"
            % (json.dumps(body, ensure_ascii=False), DECOY))


def write(folder, name, groups, mtime):
    path = pathlib.Path(folder, name)
    path.write_text(page(groups), encoding='utf-8')
    os.utime(path, (mtime, mtime))


class ParseTests(unittest.TestCase):
    def test_reads_sessions_of_each_class_with_kind_labels(self):
        classes = tkb.parse(page({'L2A': [session('2026-11-30', 'LAB 3', ['P101', 'P102'], 'LAB', ['14:00', '18:00'])]}))
        self.assertEqual(classes['L2A']['buoi'], [{'ngay': '2026-11-30', 'ten': 'LAB 3', 'loai': 'Thực hành',
                                                   'phong': ['P101', 'P102'], 'gio': ['14:00', '18:00']}])

    def test_never_reads_the_student_table(self):
        self.assertNotIn(DECOY, json.dumps(tkb.parse(page({'L2A': [session('2026-11-30')]}))))

    def test_drops_classes_without_sessions_and_malformed_sessions(self):
        classes = tkb.parse(page({'OUT': [], 'L2A': [session('2026-11-30'), {'d': '30/11', 'name': 'hỏng'}]}))
        self.assertEqual(list(classes), ['L2A'])
        self.assertEqual(len(classes['L2A']['buoi']), 1)

    def test_a_page_without_a_class_schedule_is_rejected(self):
        with self.assertRaises(ValueError):
            tkb.parse('<html><script>const STU={};</script></html>')


class MergeTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.folder = tmp.name

    def test_a_newer_file_replaces_an_older_one_on_the_days_it_covers(self):
        write(self.folder, 'cu.html', {'L2A': [session('2026-11-24', 'LEC 1'), session('2026-11-27', 'LEC 2', ['P101'])]}, 100)
        write(self.folder, 'moi.html', {'L2A': [session('2026-11-26', 'LAB 1'), session('2026-11-27', 'LEC 2', ['P205'])]}, 200)
        schedule = tkb.class_schedule(tkb.load(self.folder), 'L2A')
        self.assertEqual([(s['ngay'], s['phong'], s['nguon']) for s in schedule['buoi']],
                         [('2026-11-24', ['P101'], 'cu.html'), ('2026-11-26', ['P101'], 'moi.html'), ('2026-11-27', ['P205'], 'moi.html')])

    def test_the_weekend_after_the_last_session_is_covered_but_weekdays_are_not(self):
        write(self.folder, 'a.html', {'L2A': [session('2026-11-28')]}, 100)   # a Saturday
        write(self.folder, 'b.html', {'L2B': [session('2026-12-15')]}, 100)   # a Tuesday
        files = tkb.load(self.folder)
        self.assertIn('2026-11-29', tkb.class_schedule(files, 'L2A')['ngay_phu'])
        self.assertNotIn('2026-11-30', tkb.class_schedule(files, 'L2A')['ngay_phu'])
        self.assertNotIn('2026-12-16', tkb.class_schedule(files, 'L2B')['ngay_phu'])

    def test_a_weekend_tail_never_takes_a_day_another_file_schedules(self):
        write(self.folder, 'moi.html', {'L2A': [session('2026-11-27', 'LEC 2')]}, 200)    # ends on a Friday, saved later
        write(self.folder, 'cu.html', {'L2A': [session('2026-11-28', 'HACK')]}, 100)      # a Saturday session
        schedule = tkb.class_schedule(tkb.load(self.folder), 'L2A')
        self.assertEqual([(s['ngay'], s['nguon']) for s in schedule['buoi']], [('2026-11-27', 'moi.html'), ('2026-11-28', 'cu.html')])
        self.assertIn('2026-11-29', schedule['ngay_phu'])   # the Sunday after is covered, whichever file speaks for it

    def test_a_class_missing_from_the_newer_file_is_not_covered_on_its_days(self):
        write(self.folder, 'cu.html', {'L3A': [session('2026-11-30')]}, 100)
        write(self.folder, 'moi.html', {'T1': [session('2026-11-30')]}, 200)
        schedule = tkb.class_schedule(tkb.load(self.folder), 'L3A')
        self.assertEqual((schedule['buoi'], schedule['ngay_phu']), ([], {}))

    def test_unknown_class_and_unreadable_files(self):
        pathlib.Path(self.folder, 'hong.html').write_text('<html></html>', encoding='utf-8')
        write(self.folder, 'a.html', {'L2A': [session('2026-11-30')]}, 100)
        files = tkb.load(self.folder)
        self.assertEqual(tkb.class_codes(files), ['L2A'])
        self.assertIsNone(tkb.class_schedule(files, 'L9Z'))


class WindowTests(unittest.TestCase):
    SATURDAY = datetime.fromisoformat('2026-11-28T10:00:00+07:00')

    def test_named_windows_are_counted_from_the_question_time(self):
        expected = {'hom_nay': ('2026-11-28', '2026-11-28'), 'ngay_mai': ('2026-11-29', '2026-11-29'),
                    'tuan_nay': ('2026-11-23', '2026-11-29'), 'tuan_sau': ('2026-11-30', '2026-12-06'),
                    'sap_toi': ('2026-11-28', '2026-12-04')}
        for name, (first, last) in expected.items():
            self.assertEqual(tkb.window(self.SATURDAY, name), (date.fromisoformat(first), date.fromisoformat(last)), name)

    def test_cut_and_describe(self):
        schedule = {'lop': 'L2A', 'ten': 'L2A', 'ngay_phu': {'2026-11-28': 'a.html', '2026-11-29': 'a.html', '2026-11-30': 'b.html',
                                                             '2026-12-01': 'b.html'},
                    'buoi': [{'ngay': '2026-11-30', 'ten': 'LEC 9', 'loai': 'Lý thuyết', 'phong': ['P101'], 'gio': ['09:00', '13:00'], 'nguon': 'b.html'},
                             {'ngay': '2026-12-01', 'ten': 'LAB 9', 'loai': 'Thực hành', 'phong': ['P101', 'P102'], 'gio': ['14:00', '18:00'], 'nguon': 'b.html'}]}
        tomorrow = tkb.cut(schedule, self.SATURDAY, 'ngay_mai')   # a covered Sunday with no session
        self.assertEqual((tomorrow['ngoai_pham_vi'], tomorrow['buoi'], tomorrow['nguon']), (False, [], ['a.html']))
        self.assertIn('không có buổi nào vào Chủ nhật 29/11', tkb.describe(tomorrow))

        next_week = tkb.cut(schedule, self.SATURDAY, 'tuan_sau')  # only two days of that week are covered
        text = tkb.describe(next_week)
        self.assertEqual(next_week['nguon'], ['b.html'])
        for part in ('Thứ 2 30/11, 09:00–13:00: LEC 9 (Lý thuyết), phòng P101', 'Thứ 3 01/12, 14:00–18:00: LAB 9 (Thực hành), một trong các phòng P101, P102',
                     'chỉ ghi tới Thứ 3 01/12'):
            self.assertIn(part, text)

        far = tkb.cut(schedule, datetime.fromisoformat('2027-01-10T08:00:00+07:00'), 'tuan_nay')
        self.assertTrue(far['ngoai_pham_vi'])


if __name__ == '__main__':
    unittest.main()
