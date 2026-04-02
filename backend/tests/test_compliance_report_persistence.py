import os
import unittest
from unittest.mock import patch

from my_app.server.compliance_tools import (
    _persist_compliance_report_to_dynamodb,
    generate_compliance_report,
)


class FakeDynamoTable:
    def __init__(self):
        self.put_items = []

    def put_item(self, Item):
        self.put_items.append(Item)


class ComplianceReportPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.report = {
            "generated_at": "2026-03-24T00:00:00Z",
            "summary": {"total_standards": 1},
            "standards": [],
        }

    def test_persist_helper_skips_when_feature_flag_disabled(self):
        table = FakeDynamoTable()

        with patch.dict(os.environ, {"USE_DYNAMODB_COMPLIANCE_REPORTS": "false"}, clear=False):
            saved = _persist_compliance_report_to_dynamodb(
                report=self.report,
                standards=["gdpr"],
                include_checklist=True,
                include_penalties=True,
                include_breach_info=True,
                table=table,
            )

        self.assertFalse(saved)
        self.assertEqual(table.put_items, [])

    def test_persist_helper_writes_item_when_feature_flag_enabled(self):
        table = FakeDynamoTable()

        with patch.dict(
            os.environ,
            {
                "USE_DYNAMODB_COMPLIANCE_REPORTS": "true",
                "COMPLIANCE_REPORTS_DYNAMODB_TABLE": "SecuriVAComplianceReports",
            },
            clear=False,
        ):
            saved = _persist_compliance_report_to_dynamodb(
                report=self.report,
                standards=["GDPR", "HIPAA"],
                include_checklist=True,
                include_penalties=False,
                include_breach_info=True,
                table=table,
            )

        self.assertTrue(saved)
        self.assertEqual(len(table.put_items), 1)

        item = table.put_items[0]
        self.assertIn("report_id", item)
        self.assertEqual(item["standards"], ["gdpr", "hipaa"])
        self.assertEqual(item["options"]["include_penalties"], False)
        self.assertEqual(item["report"], self.report)

    @patch("my_app.server.compliance_tools._persist_compliance_report_to_dynamodb")
    def test_generate_compliance_report_invokes_optional_persistence(self, mock_persist):
        mock_persist.return_value = True

        result = generate_compliance_report(
            standards=["gdpr"],
            include_checklist=True,
            include_penalties=True,
            include_breach_info=True,
        )

        self.assertTrue(result["success"])
        mock_persist.assert_called_once()


if __name__ == "__main__":
    unittest.main()