import unittest

from my_app.server.guidance_catalog import GuidanceCatalog
from my_app.server.guidance_store import DynamoDBGuidanceStore
from tests.test_guidance_store import FakeDynamoTable


class GuidanceCatalogTests(unittest.TestCase):
    def setUp(self):
        self.catalog = GuidanceCatalog()

    def test_matches_gdpr_deletion_procedure(self):
        result = self.catalog.get_guidance("How do I handle a GDPR deletion request?")

        self.assertTrue(result["success"])
        self.assertEqual(result["source"]["source_type"], "procedure")
        self.assertEqual(result["source"]["source_id"], "data_deletion")
        self.assertEqual(result["source"]["regulation"], "GDPR")

    def test_matches_email_decision_tree(self):
        result = self.catalog.get_guidance("Can I email customer data to this vendor?")

        self.assertTrue(result["success"])
        self.assertEqual(result["source"]["source_type"], "decision_tree")
        self.assertEqual(result["source"]["source_id"], "email_compliance")
        self.assertEqual(result["guidance"]["start_node"], "email_received")

    def test_matches_password_example(self):
        result = self.catalog.get_guidance(
            "Show me a compliant password hashing example",
            guidance_type="example",
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["source"]["source_type"], "example")
        self.assertEqual(result["source"]["source_id"], "technical_scenarios")
        self.assertIn("password", result["guidance"]["scenario"].lower())

    def test_reports_dynamodb_backend_when_store_is_dynamodb_backed(self):
        store = DynamoDBGuidanceStore(
            table=FakeDynamoTable({
                "procedure": {
                    "data_deletion": {
                        "title": "Delete client data",
                        "description": "Procedure for deletion requests",
                        "applicable_regulations": ["GDPR"],
                        "steps": [{"step": 1, "action": "Verify request"}],
                    }
                },
                "decision_tree": {},
                "example": {},
            }),
            table_name="SecuriVAGuidanceCatalog",
        )
        catalog = GuidanceCatalog(store=store)

        result = catalog.get_guidance("How do I handle a GDPR deletion request?")

        self.assertEqual(result["source"]["backend"], "dynamodb")
        self.assertEqual(
            result["source"]["path"],
            "dynamodb://SecuriVAGuidanceCatalog/procedure/data_deletion",
        )


if __name__ == "__main__":
    unittest.main()
