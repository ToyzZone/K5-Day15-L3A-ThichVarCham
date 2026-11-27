"""Kiểm tra điều hướng bằng tin giả, không kết nối Discord."""
import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock

from discord_bot import Bot


class RoutingTests(unittest.IsolatedAsyncioTestCase):
    def make_bot(self, identity, coach):
        # Dùng lớp giả có cùng phương thức, không mở SQLite hoặc Discord client.
        bot = SimpleNamespace(
            cfg={'DISCORD_GUILD_ID': 1, 'DISCORD_QA_CHANNEL_ID': 2},
            user=SimpleNamespace(id=99), identity=lambda member: identity, coach=lambda member: coach,
            lock=asyncio.Lock(), store=SimpleNamespace(knowledge=lambda: []),
            send_text=AsyncMock())
        calls = []
        def evaluate(event, identity, kb):
            calls.append((event, identity))
            return {'noi_dung': 'Trả lời thử', 'kenh_tra': 'kenh_chung'}
        bot.evaluate = evaluate
        return bot, calls

    def message(self):
        return SimpleNamespace(author=SimpleNamespace(bot=False, id=10),
                               guild=SimpleNamespace(id=1), channel=SimpleNamespace(id=2),
                               content='!hoi XP được tính thế nào?', mentions=[], reference=None,
                               reply=AsyncMock())

    async def test_coach_can_ask_without_reply(self):
        bot, calls = self.make_bot({'vai_tro': 'lab_coach'}, True)
        await Bot.on_message(bot, self.message())
        self.assertEqual(calls[0][0]['loai'], 'cau_hoi')
        self.assertEqual(calls[0][1]['ma_hoc_vien'], 'unlinked:10')
        bot.send_text.assert_awaited_once()

    async def test_missing_role_gets_explanation(self):
        bot, calls = self.make_bot(None, False)
        message = self.message()
        await Bot.on_message(bot, message)
        self.assertEqual(calls, [])
        message.reply.assert_awaited_once()

    async def test_wrong_channel_not_processed(self):
        bot, calls = self.make_bot({'vai_tro': 'hoc_vien'}, False)
        message = self.message()
        message.channel.id = 3
        await Bot.on_message(bot, message)
        self.assertEqual(calls, [])


if __name__ == '__main__':
    unittest.main()
