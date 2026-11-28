"""Tests for the fake portal demo page served by portal_api.py. Run: python -m unittest discover -s codebase

The server listens on a free port and keeps its tokens in a temp file, so the test never touches runtime/
or an API already running on port 8765.
"""
import json
import os
import pathlib
import tempfile
import threading
import unittest
import urllib.request
from unittest import mock

import portal_api


class PortalDemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(tmp.cleanup)
        env = mock.patch.dict(os.environ, {'PORTAL_TOKENS_FILE': str(pathlib.Path(tmp.name, 'tokens.json'))})
        env.start()
        cls.addClassCleanup(env.stop)
        cls.server = portal_api.create_server(port=0)
        cls.addClassCleanup(cls.server.server_close)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.addClassCleanup(cls.server.shutdown)
        cls.base = f'http://127.0.0.1:{cls.server.server_port}'
        cls.page = cls.get('/')

    @classmethod
    def get(cls, path):
        with urllib.request.urlopen(cls.base + path, timeout=5) as response:
            return response.read().decode('utf-8')

    def test_page_is_labelled_fake_and_links_the_four_pages(self):
        self.assertIn('Portal giả · dữ liệu giả', self.page)
        for name in ('Trang tổng quan', 'Tiến độ của tôi', 'Bài nộp của tôi', 'Lịch sự kiện'):
            self.assertIn(name, self.page)

    def test_page_offers_the_three_fake_students(self):
        for code in ('HV001', 'HV002', 'HV003'):
            self.assertIn(f'<option>{code}</option>', self.page)

    def test_page_carries_nothing_from_the_real_portal(self):
        lowered = self.page.lower()
        for word in ('api keys', 'edufun', 'phoenix'):
            self.assertNotIn(word, lowered)

    def test_page_loads_nothing_from_outside(self):
        # portal_api.py serves only "/" and "/demo/api/<code>": styles, scripts, icons and fonts must be inline.
        self.assertNotRegex(self.page, r'(?i)(src|href)\s*=\s*["\']?\s*(https?:|//)')
        self.assertNotRegex(self.page, r'(?i)@import|url\(')

    def test_numbers_change_with_the_selected_student(self):
        first = json.loads(self.get('/demo/api/HV001'))
        second = json.loads(self.get('/demo/api/HV002'))
        self.assertTrue(first['du_lieu_gia'])
        self.assertNotEqual(first['du_lieu']['xp']['tong'], second['du_lieu']['xp']['tong'])


if __name__ == '__main__':
    unittest.main()
