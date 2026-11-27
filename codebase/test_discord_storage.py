"""Kiểm tra lưu qua restart, duyệt một lần và chống ghi đè bản mới."""
import tempfile
import unittest
from pathlib import Path

from knowledge_store import KnowledgeStore


class StoreTests(unittest.TestCase):
    def test_approval_history_restart_and_stale_update(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'test.db'
            store = KnowledgeStore(path, [{'ma': 'K1', 'cau_hoi': 'q', 'tra_loi': '12:00', 'nguon': 'source', 'trang_thai': 'hieu_luc'}])
            def proposal(answer, target):
                return {'loai': 'sua', 'muc_lien_quan': target, 'ban_nhap': {'cau_hoi': 'q', 'tra_loi': answer, 'nguon': 'https://discord.com/channels/1/2/3'}}
            p = store.propose('1', '2026-11-27T09:05:00+00:00', proposal('11:00', 'K1'))
            self.assertEqual(len(store.knowledge()), 1)  # chưa duyệt không thay kho
            self.assertIsNone(store.propose('1', 'later', {}))
            store.decide(p, 'coach', True)
            with self.assertRaises(ValueError):
                store.decide(p, 'coach', True)
            old = store.propose('2', '2026-11-27T09:00:00+00:00', proposal('12:00', 'D1'))
            with self.assertRaises(ValueError):
                store.decide(old, 'coach', True)
            store.close()
            store = KnowledgeStore(path, [])
            self.assertEqual([m['tra_loi'] for m in store.knowledge() if m['trang_thai'] == 'hieu_luc'], ['11:00'])
            self.assertEqual(store.knowledge()[0]['trang_thai'], 'loi_thoi')
            rejected = store.propose('3', 'now', proposal('10:00', 'D1'))
            store.decide(rejected, 'coach', False)
            self.assertEqual(len(store.knowledge()), 2)
            warning = store.propose('4', 'now', {'loai': 'canh_bao'})
            with self.assertRaises(ValueError):
                store.decide(warning, 'coach', True)
            store.close()


if __name__ == '__main__':
    unittest.main()
