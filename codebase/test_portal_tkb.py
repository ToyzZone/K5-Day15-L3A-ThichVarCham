"""Tests for the timetable endpoints of portal_api.py and portal_http.read_timetable.
Run: python -m unittest discover -s codebase

The server listens on a free port with tokens in a temp file; the timetable folder holds one made-up page.
"""
import json
import os
import pathlib
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from unittest import mock

import portal_api
import portal_http
from test_tkb import DECOY, session, write


class TimetableApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(tmp.cleanup)
        cls.folder = pathlib.Path(tmp.name, 'tkb')
        cls.folder.mkdir()
        write(cls.folder, 'mau.html', {'L2A': [session('2026-11-30', 'LEC 9')], 'L2B': [session('2026-12-01', 'LAB 9')]}, 100)
        # PORTAL_TKB_DIR is set to "" so a developer's own .env cannot switch the extension on during the "off" test.
        env = mock.patch.dict(os.environ, {'PORTAL_TOKENS_FILE': str(pathlib.Path(tmp.name, 'tokens.json')), 'PORTAL_TKB_DIR': ''})
        env.start()
        cls.addClassCleanup(env.stop)
        cls.server = portal_api.create_server(port=0)
        cls.addClassCleanup(cls.server.server_close)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.addClassCleanup(cls.server.shutdown)
        cls.base = f'http://127.0.0.1:{cls.server.server_port}'
        cls.token = cls.server.tokens['HV001']   # the fake profile HV001 is in class L2A

    def on(self):
        patcher = mock.patch.dict(os.environ, {'PORTAL_TKB_DIR': str(self.folder), 'PORTAL_API_URL': self.base})
        patcher.start()
        self.addCleanup(patcher.stop)

    def get(self, path, token=None):
        request = urllib.request.Request(self.base + path, headers={'Authorization': 'Bearer ' + (token or self.token)})
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                return response.status, response.read().decode('utf-8')
        except urllib.error.HTTPError as error:
            return error.code, error.read().decode('utf-8')

    def test_off_by_default(self):
        for path in ('/api/me/tkb', '/api/tkb/L2A'):
            self.assertEqual(self.get(path)[0], 404, path)

    def test_own_class_comes_from_the_token_and_a_named_class_from_the_path(self):
        self.on()
        status, body = self.get('/api/me/tkb')
        own = json.loads(body)
        self.assertEqual((status, own['lop'], [s['ten'] for s in own['buoi']]), (200, 'L2A', ['LEC 9']))
        other = json.loads(self.get('/api/tkb/L2B')[1])
        self.assertEqual((other['lop'], other['buoi'][0]['nguon']), ('L2B', 'mau.html'))

    def test_student_table_never_leaves_the_api(self):
        self.on()
        self.assertNotIn(DECOY, self.get('/api/me/tkb')[1] + self.get('/api/tkb/L2B')[1])

    def test_refusals(self):
        self.on()
        self.assertEqual(self.get('/api/me/tkb', token='x' * 40)[0], 401)             # no valid token
        self.assertEqual(self.get('/api/tkb/L2A?lop=L2B')[0], 400)                    # no query selectors
        status, body = self.get('/api/tkb/L9Z')
        self.assertEqual((status, json.loads(body)['lop_co']), (404, ['L2A', 'L2B'])) # unknown class: say which exist
        self.assertEqual(self.get('/api/tkb/HV002')[0], 404)                          # a student code is not a class

    def test_http_client_reads_through_the_api(self):
        self.on()
        self.assertEqual(portal_http.read_timetable(self.token, '')['lop'], 'L2A')
        self.assertEqual(portal_http.read_timetable(self.token, 'L9Z')['lop_co'], ['L2A', 'L2B'])
        self.assertEqual(portal_http.read_timetable(self.token, '../me'), {'loi': 'Mã lớp không hợp lệ.'})


if __name__ == '__main__':
    unittest.main()
