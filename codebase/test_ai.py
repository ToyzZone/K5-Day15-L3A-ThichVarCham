"""Tests for ai.py that never reach a real API. Run: python -m unittest discover -s codebase"""
import os
import tempfile
import unittest
from unittest import mock

import ai


class ModelTests(unittest.TestCase):
    def test_fake_provider_spends_no_tokens(self):
        with mock.patch.object(ai, "MODEL_PROVIDER", "fake"):
            result = ai.call_model("system", "user")
        self.assertEqual((result["model"], result["tokens_in"], result["tokens_out"]), ("fake", 0, 0))

    def test_unknown_provider_is_rejected_before_any_request(self):
        with mock.patch.multiple(ai, MODEL_PROVIDER="khac", MODEL_NAME="m", API_KEY="k"), self.assertRaises(ValueError):
            ai.call_model("system", "user")

    def test_env_file_does_not_override_existing_variables(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, ".env")
            with open(path, "w", encoding="utf-8") as f:
                f.write("# comment\nKUTE_TEST_NEW='v'\nKUTE_TEST_OLD=new\nnot a pair\n")
            with mock.patch.dict(os.environ, {"KUTE_TEST_OLD": "keep"}):
                ai.load_env(path)
                self.assertEqual((os.environ["KUTE_TEST_NEW"], os.environ["KUTE_TEST_OLD"]), ("v", "keep"))


if __name__ == "__main__":
    unittest.main()
