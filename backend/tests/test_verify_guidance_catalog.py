import unittest

from tests.verify_guidance_catalog_table import build_parity_report


class VerifyGuidanceCatalogTests(unittest.TestCase):
    def test_build_parity_report_match(self):
        local_counts = {"procedure": 5, "decision_tree": 4, "example": 4}
        dynamo_counts = {"procedure": 5, "decision_tree": 4, "example": 4}

        report = build_parity_report(local_counts, dynamo_counts)

        self.assertTrue(report["match"])
        self.assertEqual(report["total_delta"], 0)
        self.assertTrue(report["per_type"]["procedure"]["match"])

    def test_build_parity_report_mismatch(self):
        local_counts = {"procedure": 5, "decision_tree": 4, "example": 4}
        dynamo_counts = {"procedure": 5, "decision_tree": 3, "example": 4}

        report = build_parity_report(local_counts, dynamo_counts)

        self.assertFalse(report["match"])
        self.assertEqual(report["total_delta"], -1)
        self.assertFalse(report["per_type"]["decision_tree"]["match"])
        self.assertEqual(report["per_type"]["decision_tree"]["delta"], -1)


if __name__ == "__main__":
    unittest.main()
