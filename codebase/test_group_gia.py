"""Tests for group_gia.py and group_gia_web.py. Run: python -m unittest discover -s codebase

The model is always a fixed script (ScriptedModel from test_agent) and every store lives in a temp directory.
"""
import json
import pathlib
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from unittest import mock

import agent
import group_gia
import group_gia_web
from test_agent import DATA, ScriptedModel

SERVER = '42'
ENTRY = {'ma': 'D7', 'bang': 'theo_khoa', 'cau_hoi': 'Office Hour học ở phòng nào?',
         'tra_loi': 'Office Hour học ở phòng 301 nhà A, 19:00 thứ Năm.', 'nguon': 'discord://hoi-dap/77',
         'trang_thai': 'hieu_luc', 'ngay_duyet': '2026-11-27T18:30:00+00:00', 'pham_vi': {'server_id': SERVER}}
POST = 'Office Hour học ở phòng nào vậy mọi người?'
QUESTION = {'loai': 'cau_hoi_chuong_trinh'}
ANSWER_D7 = {'hanh_dong': 'tra_loi_tu_kho', 'muc_kho': 'D7', 'noi_dung': 'bịa'}


def temp_store(test, seeds=()):
    tmp = tempfile.TemporaryDirectory()
    test.addCleanup(tmp.cleanup)
    store = group_gia.GroupStore(pathlib.Path(tmp.name, 'group.db'), list(seeds))
    test.addCleanup(store.close)
    return store


class ProcessTests(unittest.TestCase):
    def setUp(self):
        self.store = temp_store(self)
        # Safety net: no test in this class may reach the real model, even outside run_post.
        patcher = mock.patch.object(agent, 'call_model', ScriptedModel())
        patcher.start()
        self.addCleanup(patcher.stop)

    def run_post(self, text, *replies, knowledge=(ENTRY,), server_id=SERVER):
        post_id = self.store.add_post('Thành viên A', text)
        model = ScriptedModel(*replies)
        with mock.patch.object(agent, 'call_model', model):
            status = group_gia.process(self.store, post_id, list(knowledge), server_id)
        return status, self.store.post(post_id), model.calls

    def test_public_entry_gets_one_comment_with_code_and_approval_date_and_no_discord_link(self):
        self.store.mark_public('D7')
        status, post, _ = self.run_post(POST, QUESTION, ANSWER_D7)
        self.assertEqual((status, post['trang_thai'], post['loai']), ('da_tra_loi', 'da_tra_loi', 'cau_hoi_chuong_trinh'))
        [comment] = post['binh_luan']
        text = comment['noi_dung']
        self.assertTrue(text.startswith('Trả lời tự động từ kho kiến thức đã duyệt'))
        self.assertIn(ENTRY['tra_loi'], text)
        self.assertIn('(Mục D7 · lab coach duyệt ngày 28/11/2026)', text)  # 18:30 UTC is the next day in Vietnam
        self.assertNotIn('bịa', text)
        self.assertNotIn('discord', text.lower())

    def test_entry_not_public_or_approved_over_a_warning_gets_no_comment_and_waits(self):
        status, post, _ = self.run_post(POST, QUESTION, ANSWER_D7)
        self.assertEqual((status, post['binh_luan']), ('cho', []))
        self.store.mark_public('D7')
        status, post, _ = self.run_post(POST, QUESTION, ANSWER_D7, knowledge=[dict(ENTRY, duyet_ghi_de=True)])
        self.assertEqual((status, post['binh_luan']), ('cho', []))

    def test_public_entry_overridden_by_an_internal_course_entry_is_not_used(self):
        fixed = dict(ENTRY, ma='K09', bang='co_dinh', ngay_duyet='2026-06-01')
        course = dict(ENTRY, ghi_de='K09', tra_loi='Office Hour chuyển sang phòng 405.')
        self.store.mark_public('K09')
        status, post, _ = self.run_post(POST, QUESTION, {'hanh_dong': 'tra_loi_tu_kho', 'muc_kho': 'K09'},
                                        knowledge=[fixed, course])
        self.assertEqual((status, post['binh_luan']), ('cho', []))

    def test_only_entries_of_this_discord_server_are_used(self):
        entry = dict(ENTRY, ngay_duyet='2026-11-09')
        self.store.mark_public('D7')
        # Same wording as the entry: the agent copies it without a model call, so only classification is scripted.
        status, post, calls = self.run_post(entry['cau_hoi'], QUESTION, knowledge=[entry])
        self.assertEqual((status, calls), ('da_tra_loi', 1))
        self.assertIn('duyệt ngày 09/11/2026', post['binh_luan'][0]['noi_dung'])
        status, post, _ = self.run_post(entry['cau_hoi'], QUESTION, knowledge=[entry], server_id='99')
        self.assertEqual((status, post['binh_luan']), ('cho', []))

    def test_official_announcement_as_best_source_waits_even_if_marked_in_the_store(self):
        self.store.mark_public('TB02')  # announcements are public only through their own record
        status, post, _ = self.run_post('Hạn nộp gate G3 là khi nào ạ?', QUESTION,
                                        {'hanh_dong': 'tra_loi_tu_kho', 'muc_kho': 'TB02'}, knowledge=[])
        self.assertEqual((status, post['binh_luan']), ('cho', []))

    def test_announcement_whose_record_says_cong_khai_can_answer(self):
        announcement = {'ma': 'TB02', 'ngay': '2026-11-20', 'noi_dung': 'Hạn gate G3 là 23:59 Chủ nhật 06/12.',
                        'link': 'discord://thong-bao/TB02', 'cong_khai': True}
        with mock.patch.object(group_gia, '_public_announcements', return_value=[announcement]):
            status, post, _ = self.run_post('Hạn nộp gate G3 là khi nào ạ?', QUESTION,
                                            {'hanh_dong': 'tra_loi_tu_kho', 'muc_kho': 'TB02'}, knowledge=[])
        self.assertEqual(status, 'da_tra_loi')
        self.assertIn(announcement['noi_dung'], post['binh_luan'][0]['noi_dung'])
        self.assertIn('TB02', post['binh_luan'][0]['noi_dung'])
        self.assertIn('20/11/2026', post['binh_luan'][0]['noi_dung'])

    def test_private_info_question_points_to_discord_without_calling_the_agent(self):
        with mock.patch.object(agent, 'answer_event') as answer_event:
            status, post, calls = self.run_post('XP của em bây giờ là bao nhiêu ạ?', {'loai': 'thong_tin_rieng'})
        answer_event.assert_not_called()
        self.assertEqual((status, calls, post['loai']), ('chi_sang_discord', 1, 'thong_tin_rieng'))
        [comment] = post['binh_luan']
        self.assertTrue(comment['noi_dung'].startswith('Trả lời tự động:'))
        self.assertIn('Discord', comment['noi_dung'])
        self.assertNotIn('discord://', comment['noi_dung'])

    def test_shared_material_is_skipped_without_comment(self):
        with mock.patch.object(agent, 'answer_event') as answer_event:
            status, post, _ = self.run_post('Chia sẻ cả nhà ghi chú buổi workshop hôm qua nhé.',
                                            {'loai': 'khong_phai_cau_hoi'})
        answer_event.assert_not_called()
        self.assertEqual((status, post['binh_luan']), ('bo_qua', []))

    def test_question_the_agent_refuses_is_skipped_without_comment(self):
        refusal = {'hanh_dong': 'tu_choi', 'ly_do_tu_choi': 'ngoai_pham_vi', 'noi_dung': 'Ngoài phạm vi.'}
        status, post, _ = self.run_post('Ai biết chỗ nào sửa laptop rẻ không?', QUESTION, refusal)
        self.assertEqual((status, post['binh_luan']), ('bo_qua', []))

    def test_unclassifiable_post_or_failing_model_waits_and_a_settled_post_is_not_processed_again(self):
        status, post, _ = self.run_post('???')  # the script is empty: the reply cannot be parsed
        self.assertEqual(status, 'cho')

        def failing_model(system, user):
            raise RuntimeError('model unavailable')
        with mock.patch.object(agent, 'call_model', failing_model):
            other = self.store.add_post('Thành viên B', POST)
            self.assertEqual(group_gia.process(self.store, other, [ENTRY], SERVER), 'cho')
        model = ScriptedModel({'loai': 'khong_phai_cau_hoi'})
        with mock.patch.object(agent, 'call_model', model):
            self.assertEqual(group_gia.process(self.store, post['id'], [ENTRY], SERVER), 'cho')
        self.assertEqual(model.calls, 0)

    def test_marking_public_then_retry_comments_on_the_waiting_post_without_reclassifying(self):
        status, post, _ = self.run_post(POST, QUESTION, ANSWER_D7)
        self.assertEqual(status, 'cho')
        self.store.mark_public('D7')
        model = ScriptedModel(ANSWER_D7)  # one reply only: a reclassification would consume it
        with mock.patch.object(agent, 'call_model', model):
            answered = group_gia.retry_waiting(self.store, [ENTRY], SERVER)
        self.assertEqual((answered, model.calls), ([post['id']], 1))
        post = self.store.post(post['id'])
        self.assertEqual((post['trang_thai'], post['loai']), ('da_tra_loi', 'cau_hoi_chuong_trinh'))
        self.assertIn('Mục D7', post['binh_luan'][0]['noi_dung'])


class StoreTests(unittest.TestCase):
    def test_seed_posts_are_loaded_once_and_listed_newest_first(self):
        seeds = json.loads(pathlib.Path(DATA, 'group_gia.json').read_text(encoding='utf-8'))
        self.assertEqual(len(seeds), 4)
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp, 'group.db')
            group_gia.GroupStore(path, seeds).close()
            store = group_gia.GroupStore(path, seeds)
            try:
                posts = store.posts()
            finally:
                store.close()
        self.assertEqual([p['noi_dung'] for p in posts], [s['noi_dung'] for s in reversed(seeds)])
        self.assertEqual({p['trang_thai'] for p in posts}, {'moi'})

    def test_waiting_message_and_internal_outcome_are_recorded(self):
        store = temp_store(self)
        post_id = store.add_post('Thành viên A', POST)
        store.set_waiting_message(post_id, '123456')
        store.set_outcome(post_id, 'noi_bo')
        post = store.post(post_id)
        self.assertEqual((post['tin_cho_duyet'], post['trang_thai'], post['binh_luan']), ('123456', 'noi_bo', []))
        self.assertEqual(store.posts('noi_bo'), [post])
        self.assertEqual(store.posts('cho'), [])


class WebTests(unittest.TestCase):
    def setUp(self):
        self.store = temp_store(self)
        self.posted, self.received = [], threading.Event()

        def on_post(post_id):
            self.posted.append((post_id, threading.get_ident()))
            self.received.set()
        self.server = group_gia_web.create_server(self.store, on_post, port=0)
        thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(thread.join)
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.url = 'http://127.0.0.1:%d' % self.server.server_port

    def request(self, path, body=None, headers=None):
        data = json.dumps(body, ensure_ascii=False).encode('utf-8') if body is not None else None
        request = urllib.request.Request(self.url + path, data, {'Content-Type': 'application/json', **(headers or {})})
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                return response.status, response.read()
        except urllib.error.HTTPError as error:
            return error.code, error.read()

    def test_post_over_http_from_another_thread_reaches_the_store_and_is_listed_with_comments(self):
        status, _ = self.request('/api/posts', {'tac_gia': 'Thành viên E', 'noi_dung': 'Office Hour ở đâu ạ?'})
        self.assertEqual(status, 201)
        self.assertTrue(self.received.wait(5))
        [(post_id, thread_id)] = self.posted
        self.assertNotEqual(thread_id, threading.get_ident())
        self.store.set_outcome(post_id, 'da_tra_loi', comment='Trả lời tự động từ kho kiến thức đã duyệt:\nPhòng 301.')
        status, body = self.request('/api/posts')
        self.assertEqual(status, 200)
        [post] = json.loads(body)['bai']
        self.assertEqual((post['id'], post['tac_gia'], post['noi_dung']), (post_id, 'Thành viên E', 'Office Hour ở đâu ạ?'))
        self.assertEqual([c['noi_dung'] for c in post['binh_luan']], ['Trả lời tự động từ kho kiến thức đã duyệt:\nPhòng 301.'])

    def test_too_long_non_json_or_foreign_host_requests_are_rejected(self):
        status, _ = self.request('/api/posts', {'tac_gia': 'A', 'noi_dung': 'x' * (group_gia_web.MAX_POST + 1)})
        self.assertEqual(status, 400)
        status, _ = self.request('/api/posts', {'tac_gia': 'A', 'noi_dung': 'hi'}, {'Content-Type': 'text/plain'})
        self.assertEqual(status, 415)
        status, _ = self.request('/api/posts', headers={'Host': 'evil.example'})
        self.assertEqual(status, 404)
        self.assertEqual((self.store.posts(), self.posted), ([], []))

    def test_page_has_the_banner_and_renders_post_data_as_text(self):
        status, body = self.request('/?van_hanh=1')
        page = body.decode('utf-8')
        self.assertEqual(status, 200)
        self.assertIn('Group giả · dữ liệu tự viết', page)
        self.assertNotIn('innerHTML', page)
        self.assertNotIn('facebook', page.lower())


if __name__ == '__main__':
    unittest.main()
