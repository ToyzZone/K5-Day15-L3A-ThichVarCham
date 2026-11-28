"""Regression coverage for consulting approved knowledge before asking for details."""
import json
import unittest
from unittest.mock import patch

import agent


class ClarificationLookupTests(unittest.TestCase):
    @staticmethod
    def ask(text):
        event = {"loai": "cau_hoi", "kenh": "hoi-dap", "noi_dung": text}
        account = {"ma_hoc_vien": "HV001"}
        return json.loads(agent.answer_event(event, account)["output"])

    def test_model_can_reconsider_after_approved_knowledge_is_found(self):
        def scripted_model(_system, payload):
            lookups = json.loads(payload)["da_tra"]
            match = next(
                (entry for lookup in lookups if lookup["cong_cu"] == "tra_kho"
                 for entry in lookup["ket_qua"] if entry["ma"] == "T01"),
                None,
            )
            decision = {"hanh_dong": "hoi_lai"}
            if match:
                decision = {"hanh_dong": "tra_loi_tu_kho", "muc_kho": match["ma"]}
            return {"text": json.dumps(decision)}

        with patch.object(agent, "call_model", side_effect=scripted_model):
            output = self.ask("Mấy giờ hết hạn nộp lab?")

        self.assertEqual(output["hanh_dong"], "tra_loi_tu_kho")
        self.assertIn("T01", output["nguon"])
        self.assertIn("22:00", output["noi_dung"])

    def test_empty_search_keeps_the_clarification_without_another_model_call(self):
        clarification = {"text": json.dumps({"hanh_dong": "hoi_lai"})}
        with (
            patch.object(agent, "call_model", return_value=clarification) as model,
            patch.object(agent, "tra_kho_kien_thuc", return_value=[]) as search,
        ):
            output = self.ask("Bạn giúp mình với")

        self.assertEqual(output["hanh_dong"], "hoi_lai")
        search.assert_called_once_with("Bạn giúp mình với")
        model.assert_called_once()
