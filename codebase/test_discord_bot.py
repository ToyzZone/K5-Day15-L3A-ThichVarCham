"""Smoke tests for discord_bot.py (needs discord.py: pip install -r requirements.txt)."""
import importlib.util
import os
import unittest
from unittest import mock

HAS_DISCORD = importlib.util.find_spec("discord") is not None
KEYS = ("DISCORD_GUILD_ID", "DISCORD_QA_CHANNEL_ID", "DISCORD_REVIEW_CHANNEL_ID", "DISCORD_LEARNER_ROLE_ID", "DISCORD_LAB_COACH_ROLE_ID")


@unittest.skipUnless(HAS_DISCORD, "discord.py is not installed")
class ConfigTests(unittest.TestCase):
    def setUp(self):
        import discord_bot
        self.bot = discord_bot

    def test_missing_settings_are_named(self):
        with mock.patch.dict(os.environ, {}, clear=True), self.assertRaisesRegex(ValueError, "DISCORD_BOT_TOKEN"):
            self.bot.config()

    def test_ids_are_read_as_numbers(self):
        env = dict({key: "42" for key in KEYS}, DISCORD_BOT_TOKEN="t")
        with mock.patch.dict(os.environ, env, clear=True):
            settings = self.bot.config()
        self.assertEqual((settings["DISCORD_GUILD_ID"], settings["DISCORD_BOT_TOKEN"]), (42, "t"))


if __name__ == "__main__":
    unittest.main()
