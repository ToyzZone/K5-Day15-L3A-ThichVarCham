"""Tests for reset_demo.py. Run: python -m unittest discover -s codebase

Every database lives in a temp directory and is built through the real store classes; no model is called.
"""
import io
import json
import sqlite3
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import reset_demo
import tools
from group_gia import GroupStore
from knowledge_store import KnowledgeStore
from reset_demo import reset

SEED = [{'ma': 'K01', 'bang': 'co_dinh', 'cau_hoi': 'Hạn nộp lab?', 'tra_loi': '23:59', 'nguon': 'l0',
         'trang_thai': 'hieu_luc'}]
POSTS = [{'tac_gia': 'An', 'noi_dung': 'Office Hour ở phòng nào?'}, {'tac_gia': 'Bình', 'noi_dung': 'Chào cả nhà'}]


def proposal():
    return {'loai': 'them', 'ly_do': 'mục mới', 'muc_lien_quan': None,
            'ban_nhap': {'cau_hoi': 'Office Hour ở đâu?', 'tra_loi': 'Phòng 301', 'nguon': 'discord://m1'}}


def rows(path, table):
    db = sqlite3.connect(path)
    try:
        return db.execute('SELECT * FROM ' + table).fetchall()
    finally:
        db.close()


class ResetTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        self.kb_path, self.group_path = self.dir / 'knowledge.db', self.dir / 'group-gia.db'
        kb = KnowledgeStore(self.kb_path, SEED)
        kb.decide(kb.propose('m1', '2026-11-27T10:00:00+00:00', proposal()), 'coach', True)  # kho gets D1
        self.max_proposal = kb.propose('m2', '2026-11-27T11:00:00+00:00', proposal())  # left pending
        kb.close()
        group = GroupStore(self.group_path, POSTS)
        group.set_outcome(1, 'da_tra_loi', comment='Trả lời tự động')
        group.mark_public('D1')
        group.close()

    def open_kb(self):
        kb = KnowledgeStore(self.kb_path, SEED)
        self.addCleanup(kb.close)
        return kb

    def test_kho_back_to_seed_and_proposal_ids_keep_counting(self):
        reset(self.dir, SEED)
        self.assertEqual(json.loads(rows(self.kb_path, 'state')[0][1]), SEED)
        self.assertEqual(rows(self.kb_path, 'proposals'), [])
        kb = self.open_kb()
        self.assertEqual(kb.knowledge(), SEED)
        self.assertGreater(kb.propose('m3', '2026-11-28T09:00:00+00:00', proposal()), self.max_proposal)

    def test_group_emptied_and_reseeded_on_next_open(self):
        reset(self.dir, SEED)
        for table in ('comments', 'posts', 'public_codes'):
            self.assertEqual(rows(self.group_path, table), [], table)
        group = GroupStore(self.group_path, POSTS)
        self.addCleanup(group.close)
        posts = group.posts()
        self.assertEqual(sorted(p['noi_dung'] for p in posts), sorted(p['noi_dung'] for p in POSTS))
        self.assertGreater(min(p['id'] for p in posts), len(POSTS))  # post ids not reused either
        self.assertEqual(group.public_codes(), set())

    def test_backup_holds_pre_reset_data(self):
        backup = reset(self.dir, SEED)
        self.assertEqual(backup.parent, self.dir)
        self.assertRegex(backup.name, r'^backup-\d{8}-\d{6}$')
        kho = json.loads(rows(backup / 'knowledge.db', 'state')[0][1])
        self.assertIn('D1', [m['ma'] for m in kho])
        self.assertEqual(len(rows(backup / 'knowledge.db', 'proposals')), 2)
        self.assertEqual(len(rows(backup / 'group-gia.db', 'posts')), len(POSTS))
        self.assertEqual(rows(backup / 'group-gia.db', 'public_codes'), [('D1',)])

    def test_works_without_group_db(self):
        self.group_path.unlink()
        backup = reset(self.dir, SEED)
        self.assertEqual(rows(self.kb_path, 'proposals'), [])
        self.assertFalse(self.group_path.exists())
        self.assertFalse((backup / 'group-gia.db').exists())

    def test_missing_knowledge_db_raises_and_changes_nothing(self):
        empty = Path(tempfile.mkdtemp(dir=self.dir))
        with self.assertRaises(FileNotFoundError):
            reset(empty, SEED)
        self.assertEqual(list(empty.iterdir()), [])

    def test_tickets_table_is_emptied(self):
        db = sqlite3.connect(self.kb_path)
        db.execute('''CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT UNIQUE,
            guild_id TEXT, owner_id TEXT, body TEXT, status TEXT DEFAULT 'draft', channel_id TEXT)''')
        db.execute("INSERT INTO tickets(source, guild_id, owner_id, body) VALUES ('m9', '1', '2', '{}')")
        db.commit()
        db.close()
        reset(self.dir, SEED)
        self.assertEqual(rows(self.kb_path, 'tickets'), [])
        db = sqlite3.connect(self.kb_path)
        new_id = db.execute("INSERT INTO tickets(source, guild_id, owner_id, body) VALUES ('m10', '1', '2', '{}')").lastrowid
        db.close()
        self.assertGreater(new_id, 1)  # ticket ids not reused

    def test_cli_prints_backup_count_and_reminders(self):
        out = io.StringIO()
        with redirect_stdout(out):
            reset_demo.main(self.dir)
        text = out.getvalue()
        backup = next(self.dir.glob('backup-*'))
        self.assertIn('Bản sao lưu: %s' % backup, text)
        self.assertIn('Kho kiến thức hiện có %d mục.' % len(tools.seed_knowledge()), text)
        self.assertIn('Khởi động lại bot', text)
        self.assertIn('kênh duyệt', text)

    def test_cli_exits_non_zero_without_knowledge_db(self):
        self.kb_path.unlink()
        with self.assertRaises(SystemExit) as cm:
            reset_demo.main(self.dir)
        self.assertIn('knowledge.db', cm.exception.code)


if __name__ == '__main__':
    unittest.main()
