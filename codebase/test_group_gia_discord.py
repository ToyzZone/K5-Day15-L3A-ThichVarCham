"""Tests for the Discord side of the fake group (waiting questions, "Duyệt và công khai"). Run: python -m unittest discover -s codebase

Discord objects are not exercised: the decisions live in plain functions of group_gia.py. Stores live in temp
directories and the model is a fixed script (ScriptedModel from test_agent).
"""
import importlib.util
import os
import pathlib
import tempfile
import unittest
from unittest import mock

import agent
import group_gia
import group_gia_web
from knowledge_store import KnowledgeStore
from test_agent import ScriptedModel
from test_group_gia import ENTRY, POST, SERVER, temp_store

HAS_DISCORD = importlib.util.find_spec('discord') is not None


class WaitingMessageTests(unittest.TestCase):
    def test_text_names_the_waiting_question_and_asks_a_lab_coach_to_reply(self):
        text = group_gia.waiting_text({'id': 12, 'noi_dung': POST})
        for part in ('Câu hỏi chờ', 'group giả', '#12', POST, 'Lab Coach', 'Reply'):
            self.assertIn(part, text)

    def test_longest_post_is_cut_to_fit_one_discord_message_without_losing_id_or_instruction(self):
        text = group_gia.waiting_text({'id': 12, 'noi_dung': 'x' * group_gia_web.MAX_POST})
        self.assertLessEqual(len(text), 2000)
        self.assertIn('#12', text.splitlines()[0])
        self.assertIn('x…', text)
        self.assertIn('Reply', text.splitlines()[-1])


class WaitingPostTests(unittest.TestCase):
    def test_replied_message_is_matched_only_to_a_post_still_waiting(self):
        store = temp_store(self)
        waiting, settled = store.add_post('Thành viên A', POST), store.add_post('Thành viên B', POST)
        store.set_outcome(waiting, 'cho')
        store.set_waiting_message(waiting, 111)
        store.set_outcome(settled, 'noi_bo')
        store.set_waiting_message(settled, 222)
        self.assertEqual(group_gia.waiting_post(store, 111)['id'], waiting)  # Discord ids are ints, the store keeps text
        self.assertIsNone(group_gia.waiting_post(store, 222))
        self.assertIsNone(group_gia.waiting_post(store, 333))


class DecisionTests(unittest.TestCase):
    def setUp(self):
        self.store = temp_store(self)
        self.post_id = self.store.add_post('Thành viên A', POST)
        self.store.set_outcome(self.post_id, 'cho')

    def outcome(self):
        return self.store.post(self.post_id)['trang_thai']

    def test_public_labels_the_new_entry_and_asks_for_a_retry_with_or_without_group_post(self):
        for proposal in ({'bai_group': self.post_id}, {}):
            self.assertTrue(group_gia.after_decision(self.store, 'public', proposal, 5))
        self.assertEqual(self.store.public_codes(), {'D5'})
        self.assertEqual(self.outcome(), 'cho')  # the retry decides whether the new entry answers it

    def test_approval_without_public_label_settles_the_waiting_post_as_internal(self):
        for action in ('approve', 'override'):  # an override approval is always internal
            self.store.set_outcome(self.post_id, 'cho')
            self.assertFalse(group_gia.after_decision(self.store, action, {'bai_group': self.post_id}, 5))
            self.assertEqual(self.outcome(), 'noi_bo')
        self.assertEqual((self.store.public_codes(), self.store.post(self.post_id)['binh_luan']), (set(), []))

    def test_reject_or_a_proposal_not_from_the_group_leaves_the_post_waiting(self):
        self.assertFalse(group_gia.after_decision(self.store, 'reject', {'bai_group': self.post_id}, 5))
        self.assertFalse(group_gia.after_decision(self.store, 'approve', {}, 6))
        self.assertEqual((self.outcome(), self.store.public_codes()), ('cho', set()))

    def test_approval_never_overwrites_a_post_answered_in_the_meantime(self):
        self.store.set_outcome(self.post_id, 'da_tra_loi', comment='Trả lời tự động từ kho kiến thức đã duyệt:\nPhòng 301.')
        group_gia.after_decision(self.store, 'approve', {'bai_group': self.post_id}, 5)
        self.assertEqual(self.outcome(), 'da_tra_loi')

    def test_public_approval_then_retry_comments_under_the_waiting_post_from_entry_d_pid(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        kb = KnowledgeStore(pathlib.Path(tmp.name, 'knowledge.db'), [])
        self.addCleanup(kb.close)
        draft = dict({k: ENTRY[k] for k in ('cau_hoi', 'tra_loi', 'nguon')},
                     pham_vi={'loai_cau_hoi': 'khac', 'server_id': SERVER})
        pid = kb.propose('m1', '2026-11-28T10:00:00+00:00', {'loai': 'them', 'ban_nhap': draft, 'bai_group': self.post_id})
        proposal = kb.pending(pid)  # read before decide, as the bot does
        kb.decide(pid, 'coach', True)
        self.assertTrue(group_gia.after_decision(self.store, 'public', proposal, pid))
        model = ScriptedModel({'hanh_dong': 'tra_loi_tu_kho', 'muc_kho': 'D%d' % pid})
        with mock.patch.object(agent, 'call_model', model):
            answered = group_gia.retry_waiting(self.store, kb.knowledge(), SERVER)
        self.assertEqual(answered, [self.post_id])
        post = self.store.post(self.post_id)
        self.assertEqual(post['trang_thai'], 'da_tra_loi')
        self.assertIn('Mục D%d' % pid, post['binh_luan'][0]['noi_dung'])


@unittest.skipUnless(HAS_DISCORD, 'discord.py is not installed')
class FlagTests(unittest.TestCase):
    def test_feature_is_off_unless_group_gia_port_is_set(self):
        import discord_bot
        env = dict({k: '42' for k in ('DISCORD_GUILD_ID', 'DISCORD_QA_CHANNEL_ID', 'DISCORD_REVIEW_CHANNEL_ID',
                                      'DISCORD_LEARNER_ROLE_ID', 'DISCORD_LAB_COACH_ROLE_ID')}, DISCORD_BOT_TOKEN='t')
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(discord_bot, 'ROOT', pathlib.Path(tmp)), \
                mock.patch.object(discord_bot, 'CHANNEL_FILE', pathlib.Path(tmp, 'none.json')):  # never read runtime/
            for extra, port in (({}, 0), ({'GROUP_GIA_PORT': ''}, 0), ({'GROUP_GIA_PORT': '8770'}, 8770)):
                with mock.patch.dict(os.environ, dict(env, **extra), clear=True):
                    self.assertEqual(discord_bot.config()['GROUP_GIA_PORT'], port)


if __name__ == '__main__':
    unittest.main()
