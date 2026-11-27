"""Tests for knowledge_fields.py. Run: python -m unittest discover -s codebase"""
import unittest

from knowledge_fields import scope_key, validate_fields

SCOPE = {"loai_cau_hoi": "deadline_bai_tap", "lop": "L3A", "bai_tap": "Lab15", "ngay": "2026-11-27"}


class FieldTests(unittest.TestCase):
    def test_only_deadlines_have_a_scope_key(self):
        self.assertIsNone(scope_key({}))
        self.assertIsNone(scope_key({"pham_vi": {"loai_cau_hoi": "khac"}}))

    def test_scope_key_ignores_case_and_spacing(self):
        a = {"pham_vi": dict(SCOPE, server_id="1")}
        b = {"pham_vi": dict(SCOPE, lop=" l3a ", server_id="1")}
        self.assertEqual(scope_key(a), scope_key(b))
        self.assertNotEqual(scope_key(a), scope_key({"pham_vi": dict(SCOPE, server_id="2")}))

    def test_deadline_is_normalised_to_vietnam_time(self):
        fields = validate_fields(dict(SCOPE, gia_tri="2026-11-27T15:00:00+00:00"), 1)
        self.assertEqual((fields["gia_tri"], fields["server_id"]), ("2026-11-27T22:00:00+07:00", "1"))

    def test_incomplete_or_ambiguous_deadlines_are_rejected(self):
        for raw in (dict(SCOPE), dict(SCOPE, gia_tri="2026-11-27T22:00"), dict(SCOPE, ngay="27/11", gia_tri="2026-11-27T22:00:00+07:00"),
                    {"lop": "L3A"}, None):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                validate_fields(raw, "1")


if __name__ == "__main__":
    unittest.main()
